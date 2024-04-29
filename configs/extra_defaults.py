from detectron2.config import CfgNode as CN

_C = CN()

# Logging
_C.CONFIG_PATH = ""
_C.TRAINING_PATHS = []
_C.VALIDATION_PATHS = []

_C.RUN_DIR = True
_C.NAME = ""

# Automatically filled do not expect values to remain
_C.LAYPA_UUID = ""
_C.LAYPA_GIT_HASH = ""
_C.SETUP_TIME = ""

# Model changes
_C.MODEL = CN()
_C.MODEL.RESUME = False
_C.MODEL.MODE = ""

_C.MODEL.SEM_SEG_HEAD = CN()
_C.MODEL.SEM_SEG_HEAD.WEIGHT = [1.0]

_C.MODEL.AMP_TRAIN = CN()
_C.MODEL.AMP_TRAIN.ENABLED = False
_C.MODEL.AMP_TRAIN.PRECISION = "bfloat16"
_C.MODEL.AMP_TEST = CN()
_C.MODEL.AMP_TEST.ENABLED = False
_C.MODEL.AMP_TEST.PRECISION = "bfloat16"

# Weights
_C.TRAIN = CN()
_C.TRAIN.WEIGHTS = ""

_C.TEST = CN()
_C.TEST.WEIGHTS = ""

# Preprocessing
_C.PREPROCESS = CN()
_C.PREPROCESS.REGION = CN()
_C.PREPROCESS.REGION.REGIONS = []
_C.PREPROCESS.REGION.MERGE_REGIONS = []
_C.PREPROCESS.REGION.REGION_TYPE = []
_C.PREPROCESS.REGION.RECTANGLE_REGIONS = []
_C.PREPROCESS.REGION.MIN_REGION_SIZE = 10

_C.PREPROCESS.BASELINE = CN()
_C.PREPROCESS.BASELINE.LINE_WIDTH = 5
_C.PREPROCESS.BASELINE.SQUARE_LINES = False

_C.PREPROCESS.RESIZE = CN()
_C.PREPROCESS.RESIZE.USE = False
_C.PREPROCESS.RESIZE.RESIZE_MODE = "shortest_edge"
_C.PREPROCESS.RESIZE.SCALING = 1.0
_C.PREPROCESS.RESIZE.RESIZE_SAMPLING = "choice"
_C.PREPROCESS.RESIZE.MIN_SIZE = [1024]
_C.PREPROCESS.RESIZE.MAX_SIZE = 2048

_C.PREPROCESS.DISABLE_CHECK = False
_C.PREPROCESS.OVERWRITE = False

_C.PREPROCESS.DPI = CN()
_C.PREPROCESS.DPI.AUTO_DETECT = False
_C.PREPROCESS.DPI.DEFAULT_DPI = 300
_C.PREPROCESS.DPI.TARGET_DPI = 300
_C.PREPROCESS.DPI.MANUAL_DPI = 300

# Input augmentations
_C.INPUT = CN()
_C.INPUT.RANDOM_FLIP = "both"

_C.INPUT.RESIZE_MODE = "shortest_edge"
_C.INPUT.SCALING = 0.0
_C.INPUT.SCALING_TRAIN = 0.5
_C.INPUT.SCALING_TEST = 0.0


_C.INPUT.DPI = CN()
_C.INPUT.DPI.AUTO_DETECT_TEST = False
_C.INPUT.DPI.DEFAULT_DPI_TEST = 300
_C.INPUT.DPI.TARGET_DPI_TEST = 300
_C.INPUT.DPI.MANUAL_DPI_TEST = 300


_C.INPUT.DPI.AUTO_DETECT_TRAIN = False
_C.INPUT.DPI.DEFAULT_DPI_TRAIN = 300
_C.INPUT.DPI.TARGET_DPI_TRAIN = 300
_C.INPUT.DPI.MANUAL_DPI_TRAIN = 300


_C.INPUT.GRAYSCALE = CN()
_C.INPUT.GRAYSCALE.PROBABILITY = 0.5

_C.INPUT.ADAPTIVE_THRESHOLDING = CN()
_C.INPUT.ADAPTIVE_THRESHOLDING.PROBABILITY = 0.5

_C.INPUT.INVERT = CN()
_C.INPUT.INVERT.PROBABILITY = 0.5
_C.INPUT.INVERT.MAX_VALUE = 255

_C.INPUT.JPEG_COMPRESSION = CN()
_C.INPUT.JPEG_COMPRESSION.PROBABILITY = 0.5
_C.INPUT.JPEG_COMPRESSION.MIN_QUALITY = 0
_C.INPUT.JPEG_COMPRESSION.MAX_QUALITY = 100

_C.INPUT.NOISE = CN()
_C.INPUT.NOISE.PROBABILITY = 0.5
_C.INPUT.NOISE.MIN_STD = 0
_C.INPUT.NOISE.MAX_STD = 50

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

_C.INPUT.HUE = CN()
_C.INPUT.HUE.PROBABILITY = 0.5
_C.INPUT.HUE.MIN_DELTA = -0.5
_C.INPUT.HUE.MAX_DELTA = 0.5

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

_C.INPUT.ORIENTATION = CN()
_C.INPUT.ORIENTATION.PROBABILITY = 1.0
_C.INPUT.ORIENTATION.PERCENTAGES = [1.0, 0.0, 0.0, 0.0]


# Solver
_C.SOLVER = CN()
# weight decay on embedding
_C.SOLVER.WEIGHT_DECAY_EMBED = 0.0
# optimizer
_C.SOLVER.OPTIMIZER = "ADAMW"
_C.SOLVER.BACKBONE_MULTIPLIER = 0.1
_C.SOLVER.AMSGRAD = True


# Added for mask2former
_C.INPUT.DATASET_MAPPER_NAME = "mask_former_semantic"
# Color augmentation
_C.INPUT.COLOR_AUG_SSD = False
# We retry random cropping until no single category in semantic segmentation GT occupies more
# than `SINGLE_CATEGORY_MAX_AREA` part of the crop.
_C.INPUT.CROP = CN()
_C.INPUT.CROP.SINGLE_CATEGORY_MAX_AREA = 1.0
# Pad image and segmentation GT in dataset mapper.
_C.INPUT.SIZE_DIVISIBILITY = -1

# mask_former model config
_C.MODEL.MASK_FORMER = CN()

# loss
_C.MODEL.MASK_FORMER.DEEP_SUPERVISION = True
_C.MODEL.MASK_FORMER.NO_OBJECT_WEIGHT = 0.1
_C.MODEL.MASK_FORMER.CLASS_WEIGHT = 1.0
_C.MODEL.MASK_FORMER.DICE_WEIGHT = 1.0
_C.MODEL.MASK_FORMER.MASK_WEIGHT = 20.0

# transformer config
_C.MODEL.MASK_FORMER.NHEADS = 8
_C.MODEL.MASK_FORMER.DROPOUT = 0.1
_C.MODEL.MASK_FORMER.DIM_FEEDFORWARD = 2048
_C.MODEL.MASK_FORMER.ENC_LAYERS = 0
_C.MODEL.MASK_FORMER.DEC_LAYERS = 6
_C.MODEL.MASK_FORMER.PRE_NORM = False

_C.MODEL.MASK_FORMER.HIDDEN_DIM = 256
_C.MODEL.MASK_FORMER.NUM_OBJECT_QUERIES = 100

_C.MODEL.MASK_FORMER.TRANSFORMER_IN_FEATURE = "res5"
_C.MODEL.MASK_FORMER.ENFORCE_INPUT_PROJ = False

# mask_former inference config
_C.MODEL.MASK_FORMER.TEST = CN()
_C.MODEL.MASK_FORMER.TEST.SEMANTIC_ON = True
_C.MODEL.MASK_FORMER.TEST.INSTANCE_ON = False
_C.MODEL.MASK_FORMER.TEST.PANOPTIC_ON = False
_C.MODEL.MASK_FORMER.TEST.OBJECT_MASK_THRESHOLD = 0.0
_C.MODEL.MASK_FORMER.TEST.OVERLAP_THRESHOLD = 0.0
_C.MODEL.MASK_FORMER.TEST.SEM_SEG_POSTPROCESSING_BEFORE_INFERENCE = False

# Sometimes `backbone.size_divisibility` is set to 0 for some backbone (e.g. ResNet)
# you can use this config to override
_C.MODEL.MASK_FORMER.SIZE_DIVISIBILITY = 32

# pixel decoder config
_C.MODEL.SEM_SEG_HEAD.MASK_DIM = 256
# adding transformer in pixel decoder
_C.MODEL.SEM_SEG_HEAD.TRANSFORMER_ENC_LAYERS = 0
# pixel decoder
_C.MODEL.SEM_SEG_HEAD.PIXEL_DECODER_NAME = "BasePixelDecoder"

# swin transformer backbone
_C.MODEL.SWIN = CN()
_C.MODEL.SWIN.PRETRAIN_IMG_SIZE = 224
_C.MODEL.SWIN.PATCH_SIZE = 4
_C.MODEL.SWIN.EMBED_DIM = 96
_C.MODEL.SWIN.DEPTHS = [2, 2, 6, 2]
_C.MODEL.SWIN.NUM_HEADS = [3, 6, 12, 24]
_C.MODEL.SWIN.WINDOW_SIZE = 7
_C.MODEL.SWIN.MLP_RATIO = 4.0
_C.MODEL.SWIN.QKV_BIAS = True
_C.MODEL.SWIN.QK_SCALE = None
_C.MODEL.SWIN.DROP_RATE = 0.0
_C.MODEL.SWIN.ATTN_DROP_RATE = 0.0
_C.MODEL.SWIN.DROP_PATH_RATE = 0.3
_C.MODEL.SWIN.APE = False
_C.MODEL.SWIN.PATCH_NORM = True
_C.MODEL.SWIN.OUT_FEATURES = ["res2", "res3", "res4", "res5"]
_C.MODEL.SWIN.USE_CHECKPOINT = False

# NOTE: maskformer2 extra configs
# transformer module
_C.MODEL.MASK_FORMER.TRANSFORMER_DECODER_NAME = "MultiScaleMaskedTransformerDecoder"

# LSJ aug
_C.INPUT.IMAGE_SIZE = 1024
_C.INPUT.MIN_SCALE = 0.1
_C.INPUT.MAX_SCALE = 2.0

# MSDeformAttn encoder configs
_C.MODEL.SEM_SEG_HEAD.DEFORMABLE_TRANSFORMER_ENCODER_IN_FEATURES = ["res3", "res4", "res5"]
_C.MODEL.SEM_SEG_HEAD.DEFORMABLE_TRANSFORMER_ENCODER_N_POINTS = 4
_C.MODEL.SEM_SEG_HEAD.DEFORMABLE_TRANSFORMER_ENCODER_N_HEADS = 8

# point loss configs
# Number of points sampled during training for a mask point head.
_C.MODEL.MASK_FORMER.TRAIN_NUM_POINTS = 112 * 112
# Oversampling parameter for PointRend point sampling during training. Parameter `k` in the
# original paper.
_C.MODEL.MASK_FORMER.OVERSAMPLE_RATIO = 3.0
# Importance sampling parameter for PointRend point sampling during training. Parametr `beta` in
# the original paper.
_C.MODEL.MASK_FORMER.IMPORTANCE_SAMPLE_RATIO = 0.75


# We retry random cropping until no single category in semantic segmentation GT occupies more
# than `SINGLE_CATEGORY_MAX_AREA` part of the crop.
_C.INPUT.CROP.SINGLE_CATEGORY_MAX_AREA = 1.0
# Used for `poly` learning rate schedule.
_C.SOLVER.POLY_LR_POWER = 0.9
_C.SOLVER.POLY_LR_CONSTANT_ENDING = 0.0
# Loss type, choose from `cross_entropy`, `hard_pixel_mining`.
_C.MODEL.SEM_SEG_HEAD.LOSS_TYPE = "hard_pixel_mining"
# DeepLab settings
_C.MODEL.SEM_SEG_HEAD.PROJECT_FEATURES = ["res2"]
_C.MODEL.SEM_SEG_HEAD.PROJECT_CHANNELS = [48]
_C.MODEL.SEM_SEG_HEAD.ASPP_CHANNELS = 256
_C.MODEL.SEM_SEG_HEAD.ASPP_DILATIONS = [6, 12, 18]
_C.MODEL.SEM_SEG_HEAD.ASPP_DROPOUT = 0.1
_C.MODEL.SEM_SEG_HEAD.USE_DEPTHWISE_SEPARABLE_CONV = False
# Backbone new configs
_C.MODEL.RESNETS = CN()
_C.MODEL.RESNETS.RES4_DILATION = 1
_C.MODEL.RESNETS.RES5_MULTI_GRID = [1, 2, 4]
# ResNet stem type from: `basic`, `deeplab`
_C.MODEL.RESNETS.STEM_TYPE = "deeplab"
