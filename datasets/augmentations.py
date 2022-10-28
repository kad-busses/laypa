# Taken from P2PaLA

import argparse
import inspect
from pathlib import Path
import pprint
import sys
from typing import Optional, Sequence
import numpy as np

import detectron2.data.transforms as T

sys.path.append(str(Path(__file__).resolve().parent.joinpath("..")))
from datasets.transforms import (ResizeTransform,
                                 VFlipTransform,
                                 HFlipTransform,
                                 WarpFieldTransform,
                                 AffineTransform,
                                 GrayscaleTransform,
                                 GaussianFilterTransform,
                                 BlendTransform)



from scipy.ndimage import map_coordinates
from scipy.ndimage import affine_transform
from scipy.ndimage import gaussian_filter

# REVIEW Use the self._init() function

class RandomApply(T.RandomApply):
    def __init__(self, tfm_or_aug, prob=0.5):
        super().__init__(tfm_or_aug, prob)
        self.tfm_or_aug = self.aug
    
    def __repr__(self):
        try:
            sig = inspect.signature(self.__init__)
            classname = type(self).__name__
            argstr = []
            for name, param in sig.parameters.items():
                assert (
                    param.kind != param.VAR_POSITIONAL and param.kind != param.VAR_KEYWORD
                ), "The default __repr__ doesn't support *args or **kwargs"
                assert hasattr(self, name), (
                    "Attribute {} not found! "
                    "Default __repr__ only works if attributes match the constructor.".format(name)
                )
                attr = getattr(self, name)
                default = param.default
                if default is attr:
                    continue
                attr_str = pprint.pformat(attr)
                if "\n" in attr_str:
                    # don't show it if pformat decides to use >1 lines
                    attr_str = "..."
                argstr.append("{}={}".format(name, attr_str))
            return "{}({})".format(classname, ", ".join(argstr))
        except AssertionError:
            return super().__repr__()

    __str__ = __repr__
    

class ResizeShortestEdge(T.Augmentation):
    """
    Resize alternative using cv2 instead of PIL or Pytorch
    """
    def __init__(self, min_size, max_size=sys.maxsize, sample_style="choice") -> None:
        super().__init__()
        assert sample_style in ["range", "choice"], sample_style
        if sample_style == "range":
            assert len(min_size) == 2, (
                    "short_edge_length must be two values using 'range' sample style."
                    f" Got {min_size}!"
                )
        if isinstance(min_size, int):
            min_size = (min_size, min_size)
        self.sample_style = sample_style
        self.min_size = min_size
        self.max_size = max_size
        

    @staticmethod
    def get_output_shape(old_height: int, old_width: int, short_edge_length: int, max_size: int) -> tuple[int, int]:
        """
        Compute the output size given input size and target short edge length.

        Args:
            old_height (int): original height of image
            old_width (int): original width of image
            short_edge_length (int): desired shortest edge length
            max_size (int): max length of other edge

        Returns:
            tuple[int, int]: new height and width
        """
        scale = float(short_edge_length) / min(old_height, old_width)
        if old_height < old_width:
            height, width = short_edge_length, scale * old_width
        else:
            height, width = scale * old_height, short_edge_length
        if max(height, width) > max_size:
            scale = max_size * 1.0 / max(height, width)
            height = height * scale
            width = width * scale

        height = int(height + 0.5)
        width = int(width + 0.5)
        return (height, width)

    def get_transform(self, image: np.ndarray) -> T.Transform:
        old_height, old_width, channels = image.shape

        if self.sample_style == "range":
            short_edge_length = np.random.randint(
                self.min_size[0], self.min_size[1] + 1)
        elif self.sample_style == "choice":
            short_edge_length = np.random.choice(self.min_size)
        else:
            raise NotImplementedError(
                "Only \"choice\" and \"range\" are accepted values")

        if short_edge_length == 0:
            return T.NoOpTransform()

        height, width = self.get_output_shape(
            old_height, old_width, short_edge_length, self.max_size)
        if (old_height, old_width) == (height, width):
            return T.NoOpTransform()

        return ResizeTransform(old_height, old_width, height, width)


class Flip(T.Augmentation):
    """
    Flip the image horizontally or vertically with the given probability.
    """

    def __init__(self, horizontal: bool=True, vertical: bool=False) -> None:
        """
        Flip the image, XOR for horizonal or vertical
        
        Args:
            horizontal (boolean): whether to apply horizontal flipping. Defaults to True.
            vertical (boolean): whether to apply vertical flipping. Defaults to False.
        """
        super().__init__()

        if horizontal and vertical:
            raise ValueError(
                "Cannot do both horiz and vert. Please use two Flip instead.")
        if not horizontal and not vertical:
            raise ValueError("At least one of horiz or vert has to be True!")
        self.horizontal = horizontal
        self.vertical = vertical

    def get_transform(self, image: np.ndarray) -> T.Transform:
        h, w = image.shape[:2]

        if self.horizontal:
            return HFlipTransform(w)
        elif self.vertical:
            return VFlipTransform(h)
        else:
            raise ValueError("At least one of horiz or vert has to be True!")

class RandomElastic(T.Augmentation):
    def __init__(self, alpha: float=0.1, sigma: float=0.01) -> None:
        """
        Args:
            alpha (int, optional): scale factor of the warpfield (sets max value). Defaults to 0.045.
            stdv (int, optional): strenght of the gaussian filter. Defaults to 0.01.
        """
        super().__init__()
        self.alpha = alpha
        self.sigma = sigma

    def get_transform(self, image: np.ndarray) -> T.Transform:
        h, w = image.shape[:2]
        
        min_length = min(h,w)
        
        warpfield = np.zeros((h, w, 2))
        dx = gaussian_filter(
            ((np.random.rand(h, w) * 2) - 1), self.sigma * min_length, mode="constant", cval=0)
        dy = gaussian_filter(
            ((np.random.rand(h, w) * 2) - 1), self.sigma * min_length, mode="constant", cval=0)
        warpfield[..., 0] = dx * min_length * self.alpha
        warpfield[..., 1] = dy * min_length * self.alpha

        return WarpFieldTransform(warpfield)


class RandomAffine(T.Augmentation):
    def __init__(self, 
                 t_stdv: float=0.02, 
                 r_kappa: float=30, 
                 sh_kappa: float=20, 
                 sc_stdv: float=0.12, 
                 probs: Optional[Sequence[float]]=None) -> None:
        super().__init__()
        self.t_stdv = t_stdv
        self.r_kappa = r_kappa
        self.sh_kappa = sh_kappa
        self.sc_stdv = sc_stdv
        
        if probs is not None:
            assert len(probs) == 4, f"{len(probs)}: {probs}"
            self.probs = probs
        else:
            self.probs = [1] * 4

    def get_transform(self, image: np.ndarray) -> T.Transform:
        
        if not any(self.probs):
            return T.NoOpTransform()

        h, w = image.shape[:2]

        center = np.eye(3)
        center[:2, 2:] = np.asarray([w, h])[:, None] / 2

        uncenter = np.eye(3)
        uncenter[:2, 2:] = -1 * np.asarray([w, h])[:, None] / 2

        matrix = np.eye(3)

        # Translation
        if self._rand_range() < self.probs[0]:
            matrix[0:2, 2] = ((np.random.rand(2) - 1) * 2) * \
                np.asarray([w, h]) * self.t_stdv

        # Rotation
        if self._rand_range() < self.probs[1]:
            rot = np.eye(3)
            theta = np.random.vonmises(0.0, self.r_kappa)
            rot[0:2, 0:2] = [[np.cos(theta), np.sin(theta)],
                            [-np.sin(theta), np.cos(theta)]]

            # print(rot)

            matrix = matrix @ center @ rot @ uncenter

        # Shear
        if self._rand_range() < self.probs[2]:
            theta1 = np.random.vonmises(0.0, self.sh_kappa)

            shear1 = np.eye(3)
            shear1[0, 1] = theta1

            # print(shear1)

            matrix = matrix @ center @ shear1 @ uncenter

            theta2 = np.random.vonmises(0.0, self.sh_kappa)

            shear2 = np.eye(3)
            shear2[1, 0] = theta2

            # print(shear2)

            matrix = matrix @ center @ shear2 @ uncenter

        # Scale
        if self._rand_range() < self.probs[3]:
            scale = np.eye(3)
            scale[0, 0], scale[1, 1] = np.exp(np.random.rand(2) * self.sc_stdv)

            # print(scale)

            matrix = matrix @ center @ scale @ uncenter

        return AffineTransform(matrix)


class RandomTranslation(T.Augmentation):
    def __init__(self, t_stdv: float=0.02) -> None:
        super().__init__()
        self.t_stdv = t_stdv

    def get_transform(self, image: np.ndarray) -> T.Transform:
        h, w = image.shape[:2]

        matrix = np.eye(3)

        # Translation
        matrix[0:2, 2] = ((np.random.rand(2) - 1) * 2) * \
            np.asarray([w, h]) * self.t_stdv

        # print(matrix)

        return AffineTransform(matrix)


class RandomRotation(T.Augmentation):
    def __init__(self, r_kappa: float=30) -> None:
        super().__init__()
        self.r_kappa = r_kappa

    def get_transform(self, image: np.ndarray) -> T.Transform:

        h, w = image.shape[:2]

        center = np.eye(3)
        center[:2, 2:] = np.asarray([w, h])[:, None] / 2

        # print(center)

        uncenter = np.eye(3)
        uncenter[:2, 2:] = -1 * np.asarray([w, h])[:, None] / 2

        # print(uncenter)

        matrix = np.eye(3)

        # Rotation
        rot = np.eye(3)
        theta = np.random.vonmises(0.0, self.r_kappa)
        rot[0:2, 0:2] = [[np.cos(theta), np.sin(theta)],
                         [-np.sin(theta), np.cos(theta)]]

        # print(rot)

        # matrix = uncenter @ rot @ center @ matrix
        matrix = matrix @ center @ rot @ uncenter

        # print(matrix)

        return AffineTransform(matrix)


class RandomShear(T.Augmentation):
    def __init__(self, sh_kappa: float=20) -> None:
        super().__init__()
        self.sh_kappa = sh_kappa

    def get_transform(self, image: np.ndarray) -> T.Transform:
        h, w = image.shape[:2]

        center = np.eye(3)
        center[:2, 2:] = np.asarray([w, h])[:, None] / 2

        uncenter = np.eye(3)
        uncenter[:2, 2:] = -1 * np.asarray([w, h])[:, None] / 2

        matrix = np.eye(3)

        # Shear1
        theta1 = np.random.vonmises(0.0, self.sh_kappa)

        shear1 = np.eye(3)
        shear1[0, 1] = theta1

        # print(shear1)

        matrix = matrix @ center @ shear1 @ uncenter

        # Shear2
        theta2 = np.random.vonmises(0.0, self.sh_kappa)

        shear2 = np.eye(3)
        shear2[1, 0] = theta2

        # print(shear2)

        matrix = matrix @ center @ shear2 @ uncenter

        return AffineTransform(matrix)


class RandomScale(T.Augmentation):
    def __init__(self, sc_stdv: float=0.12) -> None:
        super().__init__()
        self.sc_stdv = sc_stdv

    def get_transform(self, image: np.ndarray) -> T.Transform:
        h, w = image.shape[:2]

        center = np.eye(3)
        center[:2, 2:] = np.asarray([w, h])[:, None] / 2

        uncenter = np.eye(3)
        uncenter[:2, 2:] = -1 * np.asarray([w, h])[:, None] / 2

        matrix = np.eye(3)

        # Scale
        scale = np.eye(3)
        scale[0, 0], scale[1, 1] = np.exp(np.random.rand(2) * self.sc_stdv)

        # print(scale)

        matrix = matrix @ center @ scale @ uncenter

        return AffineTransform(matrix)


class Grayscale(T.Augmentation):
    """
    Randomly convert the image to grayscale
    """
    def __init__(self, image_format="RGB") -> None:
        super().__init__()
        self.image_format = image_format

    def get_transform(self, image: np.ndarray) -> T.Transform:
        return GrayscaleTransform(image_format=self.image_format)
    
class RandomGaussianFilter(T.Augmentation):
    """
    Apply random gaussian kernels
    """
    def __init__(self, min_sigma: float = 1, max_sigma: float = 3, order: int = 0, iterations: int = 1) -> None:
        super().__init__()
        self.min_sigma = min_sigma
        self.max_sigma = max_sigma
        self.order = order
        self.iterations = iterations
    
    def get_transform(self, image: np.ndarray) -> T.Transform:
        sigma = np.random.uniform(self.min_sigma, self.max_sigma)
        return GaussianFilterTransform(sigma=sigma,
                                       order=self.order,
                                       iterations=self.iterations)
        
    
class RandomSaturation(T.Augmentation):
    """
    Change the saturation of an image
    
    Saturation intensity is uniformly sampled in (intensity_min, intensity_max).
    - intensity < 1 will reduce saturation
    - intensity = 1 will preserve the input image
    - intensity > 1 will increase saturation
    """
    def __init__(self, intensity_min: float=0.5, intensity_max: float=1.5, image_format="RGB") -> None:
        """
        Args:
            intensity_min (float): Minimum augmentation
            intensity_max (float): Maximum augmentation
        """
        super().__init__()
        
        self.intensity_min = intensity_min
        self.intensity_max = intensity_max
        
        rgb_weights = np.asarray([0.299, 0.587, 0.114])
        
        if image_format == "RGB":
            self.weights = rgb_weights
        elif image_format == "BGR":
            self.weights = rgb_weights[::-1]
        else:
            raise NotImplementedError
    
    def get_transform(self, image: np.ndarray) -> T.Transform:
        grayscale = np.tile(image.dot(self.weights),
                            (3, 1, 1)).transpose((1, 2, 0)).astype(np.float32)
        
        w = np.random.uniform(self.intensity_min, self.intensity_max)
        
        return BlendTransform(grayscale, src_weight=1 - w, dst_weight=w)
    
class RandomContrast(T.Augmentation):
    """
    Randomly transforms image contrast.

    Contrast intensity is uniformly sampled in (intensity_min, intensity_max).
    - intensity < 1 will reduce contrast
    - intensity = 1 will preserve the input image
    - intensity > 1 will increase contrast

    See: https://pillow.readthedocs.io/en/3.0.x/reference/ImageEnhance.html
    """

    def __init__(self, intensity_min: float=0.5, intensity_max: float=1.5):
        """
        Args:
            intensity_min (float): Minimum augmentation
            intensity_max (float): Maximum augmentation
        """
        super().__init__()
        
        self.intensity_min = intensity_min
        self.intensity_max = intensity_max

    def get_transform(self, image):
        w = np.random.uniform(self.intensity_min, self.intensity_max)
        return BlendTransform(src_image=image.mean().astype(np.float32), src_weight=1 - w, dst_weight=w)


class RandomBrightness(T.Augmentation):
    """
    Randomly transforms image brightness.

    Brightness intensity is uniformly sampled in (intensity_min, intensity_max).
    - intensity < 1 will reduce brightness
    - intensity = 1 will preserve the input image
    - intensity > 1 will increase brightness

    See: https://pillow.readthedocs.io/en/3.0.x/reference/ImageEnhance.html
    """

    def __init__(self, intensity_min: float=0.5, intensity_max: float=1.5):
        """
        Args:
            intensity_min (float): Minimum augmentation
            intensity_max (float): Maximum augmentation
        """
        super().__init__()
        
        self.intensity_min = intensity_min
        self.intensity_max = intensity_max

    def get_transform(self, image):
        w = np.random.uniform(self.intensity_min, self.intensity_max)
        return BlendTransform(src_image=np.asarray(0).astype(np.float32), src_weight=1 - w, dst_weight=w)

def build_augmentation(cfg, is_train) -> list[T.Augmentation | T.Transform]:
    if is_train:
        min_size = cfg.INPUT.MIN_SIZE_TRAIN
        max_size = cfg.INPUT.MAX_SIZE_TRAIN
        sample_style = cfg.INPUT.MIN_SIZE_TRAIN_SAMPLING
    else:
        min_size = cfg.INPUT.MIN_SIZE_TEST
        max_size = cfg.INPUT.MAX_SIZE_TEST
        sample_style = "choice"
    augmentation: list[T.Augmentation | T.Transform] = [
        ResizeShortestEdge(min_size, max_size, sample_style)]

    if not is_train:
        return augmentation

    # TODO Add random crop
    # TODO 90 degree rotation
    
    # Color augments
    augmentation.append(RandomApply(Grayscale(image_format=cfg.INPUT.FORMAT), 
                                    prob=cfg.INPUT.GRAYSCALE.PROBABILITY))
    augmentation.append(RandomApply(RandomBrightness(intensity_min=cfg.INPUT.BRIGHTNESS.MIN_INTENSITY, 
                                                     intensity_max=cfg.INPUT.BRIGHTNESS.MAX_INTENSITY), 
                                    prob=cfg.INPUT.BRIGHTNESS.PROBABILITY))
    augmentation.append(RandomApply(RandomContrast(intensity_min=cfg.INPUT.CONTRAST.MIN_INTENSITY, 
                                                   intensity_max=cfg.INPUT.CONTRAST.MAX_INTENSITY), 
                                    prob=cfg.INPUT.CONTRAST.PROBABILITY))
    augmentation.append(RandomApply(RandomSaturation(intensity_min=cfg.INPUT.SATURATION.MIN_INTENSITY, 
                                                     intensity_max=cfg.INPUT.SATURATION.MIN_INTENSITY), 
                                    prob=cfg.INPUT.SATURATION.PROBABILITY))
    augmentation.append(RandomApply(RandomGaussianFilter(min_sigma=cfg.INPUT.GAUSSIAN_FILTER.MIN_SIGMA, 
                                                         max_sigma=cfg.INPUT.GAUSSIAN_FILTER.MAX_SIGMA), 
                                    prob=cfg.INPUT.GAUSSIAN_FILTER.PROBABILITY))
    
    # Flips
    augmentation.append(RandomApply(Flip(horizontal=True,
                                         vertical=False,), 
                                    prob=cfg.INPUT.HORIZONTAL_FLIP.PROBABILITY))
    augmentation.append(RandomApply(Flip(horizontal=True,
                                         vertical=False,), 
                                    prob=cfg.INPUT.HORIZONTAL_FLIP.PROBABILITY))
    
    
    augmentation.append(RandomApply(RandomElastic(alpha=cfg.INPUT.ELASTIC_DEFORMATION.ALPHA, 
                                                  sigma=cfg.INPUT.ELASTIC_DEFORMATION.SIGMA),
                                    prob=cfg.INPUT.ELASTIC_DEFORMATION.PROBABILITY))
    augmentation.append(RandomApply(RandomAffine(t_stdv=cfg.INPUT.AFFINE.TRANSLATION.STANDARD_DEVIATION,
                                                 r_kappa=cfg.INPUT.AFFINE.ROTATION.KAPPA,
                                                 sh_kappa=cfg.INPUT.AFFINE.SHEAR.KAPPA,
                                                 sc_stdv=cfg.INPUT.AFFINE.SCALE.STANDARD_DEVIATION,
                                                 probs=(cfg.INPUT.AFFINE.TRANSLATION.PROBABILITY,
                                                        cfg.INPUT.AFFINE.ROTATION.PROBABILITY,
                                                        cfg.INPUT.AFFINE.SHEAR.PROBABILITY,
                                                        cfg.INPUT.AFFINE.SCALE.PROBABILITY)),
                                    prob=cfg.INPUT.AFFINE.PROBABILITY))
    
    # augmentation.append(RandomApply(RandomTranslation(t_stdv=cfg.INPUT.AFFINE.TRANSLATION.STANDARD_DEVIATION),
    #                                 prob=cfg.INPUT.AFFINE.PROBABILITY * cfg.INPUT.AFFINE.TRANSLATION.PROBABILITY))
    # augmentation.append(RandomApply(RandomRotation(r_kappa=cfg.INPUT.AFFINE.ROTATION.KAPPA),
    #                                 prob=cfg.INPUT.AFFINE.PROBABILITY * cfg.INPUT.AFFINE.ROTATION.PROBABILITY))
    # augmentation.append(RandomApply(RandomShear(sh_kappa=cfg.INPUT.AFFINE.SHEAR.KAPPA),
    #                                 prob=cfg.INPUT.AFFINE.PROBABILITY * cfg.INPUT.AFFINE.SHEAR.PROBABILITY))
    # augmentation.append(RandomApply(RandomScale(sc_stdv=cfg.INPUT.AFFINE.SCALE.STANDARD_DEVIATION),
    #                                 prob=cfg.INPUT.AFFINE.PROBABILITY * cfg.INPUT.AFFINE.SCALE.PROBABILITY))
    
    
    
    # print(augmentation)
    return augmentation

def get_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Testing the image augmentation and transformations")
    io_args = parser.add_argument_group("IO")
    io_args.add_argument("-i", "--input", help="Input file",
                        required=True, type=str)

    args = parser.parse_args()
    return args




def test(args) -> None:
    import cv2
    from pathlib import Path
    from PIL import Image

    input_path = Path(args.input)

    if not input_path.is_file():
        raise FileNotFoundError(f"Image {input_path} not found")

    print(f"Loading image {input_path}")
    image = cv2.imread(str(input_path))[..., ::-1]

    resize = ResizeShortestEdge(min_size=(640, 672, 704, 736, 768, 800),
                                max_size=1333, 
                                sample_style="choice")
    elastic = RandomElastic()

    affine = RandomAffine()
    translation = RandomTranslation()
    rotation = RandomRotation()
    shear = RandomShear()
    scale = RandomScale()
    grayscale = Grayscale()
    
    gaussian = RandomGaussianFilter()
    contrast = RandomContrast()
    brightness = RandomBrightness()
    saturation = RandomSaturation()
    
    augs = []

    # augs = T.AugmentationList([resize, elastic, affine])

    augs.append(resize)
    augs.append(elastic)
    # augs.append(grayscale)
    # augs.append(contrast)
    # augs.append(brightness)
    # augs.append(saturation)
    # augs.append(gaussian)
    # augs.append(affine)
    # augs.append(translation)
    # augs.append(rotation)
    # augs.append(shear)
    # augs.append(scale)
    
    
    
    augs_list = T.AugmentationList(augs=augs)

    input_augs = T.AugInput(image)

    transforms = augs_list(input_augs)

    output_image = input_augs.image


    im = Image.fromarray(image)
    im.show("Original")

    im = Image.fromarray(output_image.round().clip(0, 255).astype(np.uint8))
    im.show("Transformed")


if __name__ == "__main__":
    args = get_arguments()
    test(args)
