import argparse
import json
from pathlib import Path
import sys
import numpy as np

sys.path.append(str(Path(__file__).resolve().parent.joinpath("..")))
from page_xml.xmlPAGE import PageData
from page_xml.xml_regions import XMLRegions
from typing import Optional


def get_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(parents=[XMLConverter.get_parser()],
        description="Code to turn an xml file into an array")
    io_args = parser.add_argument_group("IO")
    io_args.add_argument("-i", "--input", help="Input file",
                        required=True, type=str)
    io_args.add_argument(
        "-o", "--output", help="Output file", required=True, type=str)

    args = parser.parse_args()
    return args

# IDEA have fixed ordering of the classes, maybe look at what order is best
class XMLConverter(XMLRegions):
    """
    Class for turning a pageXML into an image with classes (for segmentation)
    """
    def __init__(self, mode: str, 
                 line_width: Optional[int] = None,
                 regions: Optional[list[str]] = None, 
                 merge_regions: Optional[list[str]] = None, 
                 region_type: Optional[list[str]] = None) -> None:
        """
        Class for turning a pageXML into an image with classes
        
        Args:
            mode (str): mode of the region type
            line_width (Optional[int], optional): width of line. Defaults to None.
            line_color (Optional[int], optional): value of line (when only one line type exists). Defaults to None.
            regions (Optional[list[str]], optional): list of regions to extract from pageXML. Defaults to None.
            merge_regions (Optional[list[str]], optional): list of region to merge into one. Defaults to None.
            region_type (Optional[list[str]], optional): type of region for each region. Defaults to None.
        """
        super().__init__(mode, line_width, regions, merge_regions, region_type)

    def to_image(self, xml_path: Path, original_image_shape=None, image_shape=None) -> np.ndarray:
        """
        Turn a single pageXML into a mask of labels

        Args:
            xml_path (Path): path to pageXML
            original_image_shape (tuple, optional): shape of the corresponding image. Defaults to None.
            image_shape (tuple, optional): shape of the corresponding image. Defaults to None.

        Raises:
            NotImplementedError: mode is not known

        Returns:
            np.ndarray: mask of labels
        """
        gt_data = PageData(xml_path)
        gt_data.parse()
        
        if original_image_shape is not None:
            gt_data.set_size(original_image_shape)

        if image_shape is None:
            image_shape = gt_data.get_size()
        if self.mode == "region":
            region_mask = gt_data.build_region_mask(
                image_shape,
                set(self.region_types.values()),
                self.region_classes
            )
            return region_mask
        elif self.mode == "baseline":
            baseline_mask = gt_data.build_baseline_mask(
                image_shape,
                line_width=self.line_width
            )
            return baseline_mask
        elif self.mode == "start":
            start_mask = gt_data.build_start_mask(
                image_shape,
                line_width=self.line_width
            )
            return start_mask
        elif self.mode == "end":
            end_mask = gt_data.build_end_mask(
                image_shape,
                line_width=self.line_width
            )
            return end_mask
        elif self.mode == "separator":
            separator_mask = gt_data.build_separator_mask(
                image_shape,
                line_width=self.line_width
            )
            return separator_mask
        elif self.mode == "baseline_separator":
            baseline_separator_mask = gt_data.build_baseline_separator_mask(
                image_shape,
                line_width=self.line_width
            )
            return baseline_separator_mask
        else:
            raise NotImplementedError

    def to_json(self, xml_path: Path, original_image_shape=None, image_shape=None) -> list:
        """
        Turn a single pageXML into a dict with scaled coordinates

        Args:
            xml_path (Path): path to pageXML
            original_image_shape (tuple, optional): shape of the corresponding image. Defaults to None.
            image_shape (tuple, optional): shape of the corresponding image. Defaults to None.

        Raises:
            NotImplementedError: mode is not known

        Returns:
            dict: scaled coordinates about the location of the objects in the image
        """
        gt_data = PageData(xml_path)
        gt_data.parse()
        
        if original_image_shape is not None:
            gt_data.set_size(original_image_shape)

        if image_shape is None:
            image_shape = gt_data.get_size()
            
        if self.mode == "region":
            instances = gt_data.build_region_instances(
                image_shape,
                set(self.region_types.values()),
                self.region_classes
            )
            return instances
        elif self.mode == "baseline":
            instances = gt_data.build_baseline_instances(
                image_shape,
                self.line_width
            )
            return instances
        else:
            raise NotImplementedError
        
    def to_pano(self, xml_path: Path, original_image_shape=None, image_shape=None) -> tuple[np.ndarray, list]:
        """
        Turn a single pageXML into a pano image with corresponding pixel info

        Args:
            xml_path (Path): path to pageXML
            original_image_shape (tuple, optional): shape of the corresponding image. Defaults to None.
            image_shape (tuple, optional): shape of the corresponding image. Defaults to None.

        Raises:
            NotImplementedError: mode is not known

        Returns:
            dict: scaled coordinates about the location of the objects in the image
        """
        gt_data = PageData(xml_path)
        gt_data.parse()
        
        if original_image_shape is not None:
            gt_data.set_size(original_image_shape)

        if image_shape is None:
            image_shape = gt_data.get_size()
            
        if self.mode == "region":
            pano_mask, segments_info = gt_data.build_region_pano(
                image_shape,
                set(self.region_types.values()),
                self.region_classes
            )
            return pano_mask, segments_info
        elif self.mode == "baseline":
            pano_mask, segments_info = gt_data.build_baseline_pano(
                image_shape,
                self.line_width
            )
            return pano_mask, segments_info
        else:
            raise NotImplementedError

if __name__ == "__main__":
    args = get_arguments()
    XMLConverter(
        mode=args.mode,
        line_width=args.line_width,
        regions=args.regions,
        merge_regions=args.merge_regions,
        region_type=args.region_type
    )

    input_path = Path(args.input)
    output_path = Path(args.output)
    
    
    
    