import argparse
from datetime import datetime
import os
from pathlib import Path
import sys
from typing import List, Optional
import torch

import datasets.dataset as dataset
from configs.defaults import _C as _C_default
from configs.extra_defaults import _C as _C_extra


from detectron2.data import (
    MetadataCatalog,
    build_detection_test_loader,
    build_detection_train_loader,
    DatasetMapper
)
from detectron2.engine import DefaultTrainer
from detectron2.checkpoint import DetectionCheckpointer
from detectron2.config import (
    get_cfg,
    CfgNode
)
from detectron2.evaluation import SemSegEvaluator
from detectron2.utils.events import EventStorage
from detectron2.data import transforms as T
from detectron2.engine import hooks, launch


from datasets.augmentations import build_augmentation
from utils.path_utils import unique_path

# TODO Replace with LazyConfig

# torch.autograd.set_detect_anomaly(True)

def get_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Main file for Layout Analysis")

    detectron2_args = parser.add_argument_group("detectron2")

    detectron2_args.add_argument(
        "-c", "--config", help="config file", required=True)
    detectron2_args.add_argument(
        "--opts", nargs=argparse.REMAINDER, help="optional args to change", default=[])

    io_args = parser.add_argument_group("IO")
    io_args.add_argument("-t", "--train", help="Train input folder",
                            required=True, type=str)
    io_args.add_argument("-v", "--val", help="Validation input folder",
                            required=True, type=str)
    # other_args.add_argument("--img_list", help="List with location of images")
    # other_args.add_argument("--label_list", help="List with location of labels")
    # other_args.add_argument("--out_size_list", help="List with sizes of images")
    
    # From detectron2.engine.defaults
    gpu_args = parser.add_argument_group("GPU Launch")
    gpu_args.add_argument("--num-gpus", type=int, default=1, help="number of gpus *per machine*")
    gpu_args.add_argument("--num-machines", type=int, default=1, help="total number of machines")
    gpu_args.add_argument(
        "--machine-rank", type=int, default=0, help="the rank of this machine (unique per machine)"
    )

    # PyTorch still may leave orphan processes in multi-gpu training.
    # Therefore we use a deterministic way to obtain port,
    # so that users are aware of orphan processes by seeing the port occupied.
    port = 2**15 + 2**14 + hash(os.getuid() if sys.platform != "win32" else 1) % 2**14
    gpu_args.add_argument(
        "--dist-url",
        default="tcp://127.0.0.1:{}".format(port),
        help="initialization URL for pytorch distributed backend. See "
        "https://pytorch.org/docs/stable/distributed.html for details.",
    )

    args = parser.parse_args()

    return args


def setup_cfg(args, cfg: Optional[CfgNode] = None, save_config=True) -> CfgNode:
    if cfg is None:
        cfg = _C_default

    # Merge with extra defaults, config file and command line args
    cfg.set_new_allowed(True)
    cfg.merge_from_other_cfg(_C_extra)
    cfg.set_new_allowed(False)

    cfg.merge_from_file(args.config)
    cfg.merge_from_list(args.opts)
    
    
    # For saving/documentation purposes
    now = datetime.now()
    formatted_datetime = f"{now:%Y-%m-%d_%H-%M-%S}"
    cfg.SETUP_TIME = formatted_datetime
    
    cfg.CONFIG_PATH = str(Path(args.config).resolve())
    
    
    # Setup run specific folders to prevent overwrites
    if cfg.OUTPUT_DIR and (cfg.RUN_DIR or cfg.NAME) and not cfg.MODEL.RESUME:
        folder_name = []
        if cfg.RUN_DIR:
            folder_name.append(f"RUN_{formatted_datetime}")
        if cfg.NAME:
            folder_name.append(cfg.NAME)
        cfg.OUTPUT_DIR = os.path.join(cfg.OUTPUT_DIR, "_".join(folder_name))
    
    
    if cfg.MODEL.DEVICE:
        # If device can not be found, default to cpu
        if torch.cuda.device_count() == 0:
            cfg.MODEL.DEVICE = 'cpu'
    else:
        # If not specified use cuda if possible
        if torch.cuda.device_count() > 0:
            cfg.MODEL.DEVICE = 'cuda'
        else:
            cfg.MODEL.DEVICE = 'cpu'

    cfg.freeze()
    
    # Save the confic with all (changed) parameters to a yaml
    if save_config:
        os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
        cfg_output_path = Path(cfg.OUTPUT_DIR).joinpath("config.yaml")
        cfg_output_path = unique_path(cfg_output_path)
        with open(cfg_output_path, mode="w") as f:
            f.write(cfg.dump())
    return cfg


class Trainer(DefaultTrainer):
    
    def __init__(self, cfg):
        super().__init__(cfg)
        
        self.checkpointer.save_dir = os.path.join(cfg.OUTPUT_DIR, "checkpoints")
        os.makedirs(self.checkpointer.save_dir, exist_ok=True)
        
        
        miou_checkpointer = hooks.BestCheckpointer(eval_period=cfg.TEST.EVAL_PERIOD, 
                                                   checkpointer=self.checkpointer,
                                                   val_metric="sem_seg/mIoU",
                                                   mode='max',
                                                   file_prefix='model_best_mIoU')
        
        fwiou_checkpointer = hooks.BestCheckpointer(eval_period=cfg.TEST.EVAL_PERIOD, 
                                                   checkpointer=self.checkpointer,
                                                   val_metric="sem_seg/fwIoU",
                                                   mode='max',
                                                   file_prefix='model_best_fwIoU')
        
        macc_checkpointer = hooks.BestCheckpointer(eval_period=cfg.TEST.EVAL_PERIOD, 
                                                   checkpointer=self.checkpointer,
                                                   val_metric="sem_seg/mACC",
                                                   mode='max',
                                                   file_prefix='model_best_mACC')
        
        pacc_checkpointer = hooks.BestCheckpointer(eval_period=cfg.TEST.EVAL_PERIOD, 
                                                   checkpointer=self.checkpointer,
                                                   val_metric="sem_seg/pACC",
                                                   mode='max',
                                                   file_prefix='model_best_pACC')
        
        self.register_hooks([miou_checkpointer, 
                             fwiou_checkpointer, 
                             macc_checkpointer, 
                             pacc_checkpointer])

    @classmethod
    def build_evaluator(cls, cfg, dataset_name):
        sem_seg_output_dir = os.path.join(cfg.OUTPUT_DIR, "semantic_segmentation")
        evaluator_type = MetadataCatalog.get(dataset_name).evaluator_type
        if evaluator_type == "sem_seg":
            evaluator = SemSegEvaluator(
                dataset_name=dataset_name,
                distributed=True,
                output_dir=sem_seg_output_dir
            )
        else:
            raise NotImplementedError(
                f"Current evaluator type {evaluator_type} not supported")

        return evaluator

    @classmethod
    def build_train_loader(cls, cfg):
        if "SemanticSegmentor" in cfg.MODEL.META_ARCHITECTURE:
            mapper = DatasetMapper(is_train=True,
                                   augmentations=build_augmentation(
                                       cfg, is_train=True),
                                   image_format=cfg.INPUT.FORMAT,
                                   use_instance_mask=cfg.MODEL.MASK_ON,
                                   instance_mask_format=cfg.INPUT.MASK_FORMAT,
                                   use_keypoint=cfg.MODEL.KEYPOINT_ON)
        else:
            raise NotImplementedError(
                f"Current META_ARCHITECTURE type {cfg.MODEL.META_ARCHITECTURE} not supported")

        return build_detection_train_loader(cfg=cfg, mapper=mapper)

    @classmethod
    def build_test_loader(cls, cfg, dataset_name):
        if "SemanticSegmentor" in cfg.MODEL.META_ARCHITECTURE:
            mapper = DatasetMapper(is_train=False,
                                   augmentations=build_augmentation(
                                       cfg, is_train=False),
                                   image_format=cfg.INPUT.FORMAT,
                                   use_instance_mask=cfg.MODEL.MASK_ON,
                                   instance_mask_format=cfg.INPUT.MASK_FORMAT,
                                   use_keypoint=cfg.MODEL.KEYPOINT_ON)
        else:
            raise NotImplementedError(
                f"Current META_ARCHITECTURE type {cfg.MODEL.META_ARCHITECTURE} not supported")

        return build_detection_test_loader(cfg=cfg, mapper=mapper, dataset_name=dataset_name)


def main(args) -> None:

    # get("../configs/Misc/semantic_R_50_FPN_1x.yaml")

    cfg = setup_cfg(args)

    dataset.register_dataset(args.train, args.val, "train", "val", mode=cfg.MODEL.MODE)
    
    trainer = Trainer(cfg=cfg)
    if not cfg.TRAIN.WEIGHTS:
        trainer.resume_or_load(resume=cfg.MODEL.RESUME)
    else:
        trainer.checkpointer.load(cfg.TRAIN.WEIGHTS)
        if trainer.checkpointer.has_checkpoint():
            trainer.start_iter = trainer.iter + 1

    # print(trainer.model)

    with EventStorage() as storage:
        return trainer.train()


if __name__ == "__main__":
    args = get_arguments()
    # main(args)
    
    assert args.num_gpus <= torch.cuda.device_count(), \
        f"Less GPUs found ({torch.cuda.device_count()}) than specified ({args.num_gpus})"
    
    launch(
        main,
        num_gpus_per_machine=args.num_gpus,
        num_machines=args.num_machines,
        machine_rank=args.machine_rank,
        dist_url=args.dist_url,
        args=(args,)
    )
