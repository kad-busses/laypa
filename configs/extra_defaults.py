from detectron2.config import CfgNode as CN

_C = CN()

_C.RUN_DIR = True
_C.SETUP_TIME = ""

_C.MODEL = CN()
_C.MODEL.RESUME = False
_C.MODEL.MODE = ""

_C.TRAIN = CN()
_C.TRAIN.WEIGHTS = ""

_C.TEST = CN()
_C.TEST.WEIGHTS = ""

_C.INPUT = CN()
_C.INPUT.RANDOM_FLIP = "both"

_C.INPUT.GRAYSCALE = CN()
_C.INPUT.GRAYSCALE.PROBABILITY = 0.5

_C.INPUT.BRIGHTNESS = CN()
_C.INPUT.BRIGHTNESS.PROBABILITY = 0.5
_C.INPUT.BRIGHTNESS.MIN_INTENSITY = 0.5
_C.INPUT.BRIGHTNESS.MAX_INTENSITY = 1.5

_C.INPUT.CONTRAST = CN()
_C.INPUT.CONTRAST.PROBABILITY = 0.5
_C.INPUT.CONTRAST.MIN_INTENSITY = 0.5
_C.INPUT.CONTRAST.MAX_INTENSITY = 1.5

_C.INPUT.SATURATION = CN()
_C.INPUT.SATURATION.PROBABILITY = 0.5
_C.INPUT.SATURATION.MIN_INTENSITY = 0.5
_C.INPUT.SATURATION.MAX_INTENSITY = 1.5

_C.INPUT.GAUSSIAN_FILTER = CN()
_C.INPUT.GAUSSIAN_FILTER.PROBABILITY = 0.5
_C.INPUT.GAUSSIAN_FILTER.MIN_SIGMA = 0.0
_C.INPUT.GAUSSIAN_FILTER.MAX_SIGMA = 3.0

_C.INPUT.HORIZONTAL_FLIP = CN()
_C.INPUT.HORIZONTAL_FLIP.PROBABILITY = 0.5

_C.INPUT.VERTICAL_FLIP = CN()
_C.INPUT.VERTICAL_FLIP.PROBABILITY = 0.5

_C.INPUT.ELASTIC_DEFORMATION = CN()
_C.INPUT.ELASTIC_DEFORMATION.PROBABILITY = 0.5
_C.INPUT.ELASTIC_DEFORMATION.ALPHA = 0.1
_C.INPUT.ELASTIC_DEFORMATION.SIGMA = 0.01

_C.INPUT.AFFINE = CN()
_C.INPUT.AFFINE.PROBABILITY = 0.5

_C.INPUT.AFFINE.TRANSLATION = CN()
_C.INPUT.AFFINE.TRANSLATION.PROBABILITY = 0.5
_C.INPUT.AFFINE.TRANSLATION.STANDARD_DEVIATION = 0.02

_C.INPUT.AFFINE.ROTATION = CN()
_C.INPUT.AFFINE.ROTATION.PROBABILITY = 0.5
_C.INPUT.AFFINE.ROTATION.KAPPA = 30.0

_C.INPUT.AFFINE.SHEAR = CN()
_C.INPUT.AFFINE.SHEAR.PROBABILITY = 0.5
_C.INPUT.AFFINE.SHEAR.KAPPA = 20.0

_C.INPUT.AFFINE.SCALE = CN()
_C.INPUT.AFFINE.SCALE.PROBABILITY = 0.5
_C.INPUT.AFFINE.SCALE.STANDARD_DEVIATION = 0.12


