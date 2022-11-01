import argparse
import logging
from multiprocessing import Pool
import os
import string
import sys
from typing import Optional
import numpy as np
from pathlib import Path
import uuid

from xml_regions import XMLRegions
from tqdm import tqdm
import cv2

sys.path.append(str(Path(__file__).resolve().parent.joinpath("..")))
from utils.copy import copy_mode
from utils.path import clean_input
from page_xml.xmlPAGE import PageData

def get_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(parents=[XMLRegions.get_parser()],
        description="Generate pageXML from label mask and images")
    
    io_args = parser.add_argument_group("IO")
    io_args.add_argument("-a", "--mask", help="Input mask folder/files", nargs="+", default=[],
                        required=True, type=str)
    io_args.add_argument("-i", "--input", help="Input image folder/files", nargs="+", default=[],
                        required=True, type=str)
    io_args.add_argument(
        "-o", "--output", help="Output folder", required=True, type=str)

    args = parser.parse_args()
    return args

class GenPageXML(XMLRegions):
    
    def __init__(self, output_dir: str|Path,
                 mode: str,
                 line_width: Optional[int] = None,
                 line_color: Optional[int] = None,
                 regions: Optional[list[str]] = None,
                 merge_regions: Optional[list[str]] = None,
                 region_type: Optional[list[str]] = None) -> None:
        super().__init__(mode, line_width, line_color, regions, merge_regions, region_type)
        
        self.logger = logging.getLogger(__name__)
        
        if isinstance(output_dir, str):
            output_dir = Path(output_dir)
            
        if not output_dir.is_dir():
            print(f"Could not find output dir ({output_dir}), creating one at specified location")
            output_dir.mkdir(parents=True)
        self.output_dir = output_dir
        
        page_dir = self.output_dir.joinpath("page")
        if not page_dir.is_dir():
            print(f"Could not find page dir ({page_dir}), creating one at specified location")
            page_dir.mkdir(parents=True)
        self.page_dir = page_dir
        
        self.regions = self.get_regions()
    
    def generate_single_page(self, info: tuple[np.ndarray|Path, Path]):
        mask, image_path = info
        
        if isinstance(mask, Path):
            mask = cv2.imread(str(mask), cv2.IMREAD_GRAYSCALE)
        
        xml_output_path = self.page_dir.joinpath(image_path.stem + ".xml")
        image_output_path = self.output_dir.joinpath(image_path.name)
        
        copy_mode(image_path, image_output_path, mode="symlink")
        
        old_height, old_width, channels = cv2.imread(str(image_output_path)).shape
        
        height, width = mask.shape
        
        scaling = np.asarray([width, height]) / np.asarray([old_width, old_height])
        
        page = PageData(xml_output_path, logger=self.logger)
        page.new_page(image_output_path.name, str(old_height), str(old_width))
        
        region_id = 0
        
        for i, region in enumerate(self.regions):
            if region == "background":
                continue
            binary_region_mask = np.zeros_like(mask)
            binary_region_mask[mask == i] = 1
            
            region_type = self.region_types[region]
            
            contours, hierarchy = cv2.findContours(
                binary_region_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            for cnt in contours:
                # --- remove small objects
                if cnt.shape[0] < 4:
                    continue
                # TODO what size
                # if cv2.contourArea(cnt) < size:
                #     continue
                
                region_id += 1
                
                # --- soft a bit the region to prevent spikes
                epsilon = 0.005 * cv2.arcLength(cnt, True)
                approx_poly = cv2.approxPolyDP(cnt, epsilon, True)
            
                approx_poly = np.round((approx_poly * scaling)).astype(np.int32)
                
                region_coords = ""
                for coords in approx_poly.reshape(-1, 2):
                    region_coords = region_coords + f" {coords[0]},{coords[1]}"
                region_coords = region_coords.strip()
                
                _uuid = uuid.uuid4()
                text_reg = page.add_element(
                    region_type, f"region_{uuid}_{region_id}", region, region_coords
                )
                
        page.save_xml()
        
    def run(self, 
            mask_list: list[np.ndarray] | list[Path], 
            image_path_list: list[Path]) -> None:
        
        if len(mask_list) != len(image_path_list):
            raise ValueError(f"masks must match image paths in length: {len(mask_list)} v. {len(image_path_list)}")
        
        # #Single thread
        # for mask_i, image_path_i in tqdm(zip(mask_list, image_path_list), total=len(mask_list)):
        #     self.generate_single_page((mask_i, image_path_i))
        
        # Multi thread
        with Pool(os.cpu_count()) as pool:
            _ = list(tqdm(pool.imap_unordered(
                self.generate_single_page, list(zip(mask_list, image_path_list))), total=len(mask_list)))

def main(args):
    # Formats found here: https://docs.opencv.org/4.x/d4/da8/group__imgcodecs.html#imread
    image_formats = [".bmp", ".dib",
                     ".jpeg", ".jpg", ".jpe",
                     ".jp2",
                     ".png",
                     ".webp",
                     ".pbm", ".pgm", ".ppm", ".pxm", ".pnm",
                     ".pfm",
                     ".sr", ".ras",
                     ".tiff", ".tif",
                     ".exr",
                     ".hdr", ".pic"]
    mask_paths = clean_input(args.mask, suffixes=[".png"])
    image_paths = clean_input(args.input, suffixes=image_formats)
    
    gen_page = GenPageXML(output_dir=args.output,
                          mode=args.mode,
                          line_width=args.line_width,
                          line_color=args.line_color,
                          regions=args.regions,
                          merge_regions=args.merge_regions,
                          region_type=args.region_type)
    
    gen_page.run(mask_paths, image_paths)
    
    
    
if __name__ == "__main__":
    args = get_arguments()
    main(args)
    
        