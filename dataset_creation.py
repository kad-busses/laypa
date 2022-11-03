import argparse
from collections import Counter
import errno
from glob import glob
import os
from pathlib import Path
import shutil
from sklearn.model_selection import train_test_split
from natsort import os_sorted
from datetime import datetime
from utils.copy_utils import copy_mode
from utils.path_utils import image_path_to_xml_path

def get_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Moving files from multiple folders into a single structured dataset")
    
    io_args = parser.add_argument_group("IO")
    io_args.add_argument("-i", "--input", help="Input folder",
                        required=True, type=str)
    io_args.add_argument("-o", "--output", help="Output folder",
                        required=True, type=str)
    
    parser.add_argument("-m", "--mode", choices=["link", "symlink", "copy"], help="Mode for moving the images", default='copy')
    
    args = parser.parse_args()
    return args
def copy_paths(paths: list[Path], output_dir, mode="copy") -> list[Path]:
    print(len(paths))
    if not output_dir.is_dir():
        print(f"Could not find output dir ({output_dir}), creating one at specified location")
        output_dir.mkdir(parents=True)
    
    page_dir = output_dir.joinpath("page")
    
    if not page_dir.is_dir():
        print(f"Could not find output page dir ({page_dir}), creating one at specified location")
        page_dir.mkdir(parents=True)
        
    output_paths = []
    for path in paths:
        page_path = image_path_to_xml_path(path)
        output_path = output_dir.joinpath(path.name)
        output_page_path = page_dir.joinpath(page_path.name)
        copy_mode(path, output_path, mode=mode)
        copy_mode(page_path, output_page_path, mode=mode)
        
        output_paths.append(output_path)
        
    return output_paths

def main(args):
    if args.input == "":
        raise ValueError("Must give an input")
    if args.output == "":
        raise ValueError("Must give an output")
    
    input_path = Path(args.input)
    
    if not input_path.exists():
        raise FileNotFoundError(f"{input_path} does not exist")
    
    # IDEA add more image formats
    # image_formats = [".bmp", ".dib",
    #                  ".jpeg", ".jpg", ".jpe",
    #                  ".jp2",
    #                  ".png",
    #                  ".webp",
    #                  ".pbm", ".pgm", ".ppm", ".pxm", ".pnm",
    #                  ".pfm",
    #                  ".sr", ".ras",
    #                  ".tiff", ".tif",
    #                  ".exr",
    #                  ".hdr", ".pic"]
    
    
    image_format = '.jpg'
    
    # Find all images
    all_image_paths = list(input_path.glob(f"**/**/*{image_format}")) # Assume depth 2
    
    
    if len(all_image_paths) != len(set(path.stem for path in all_image_paths)):
        duplicates = {k:v for k, v in Counter(path.stem for path in all_image_paths).items() if v > 1}
        
        print(os_sorted(duplicates.items(), key=lambda s: s[0]))
        raise ValueError("Found duplicate stems for images")
    
    if len(all_image_paths) == 0:
        raise FileNotFoundError(f"No images found within {input_path}")
    
    train_paths, val_test_paths = train_test_split(all_image_paths, test_size=0.2)
    
    val_paths, test_paths = train_test_split(val_test_paths, test_size=0.5)
    
    print("Number of train images:", len(train_paths))
    print("Number of validation images:", len(val_paths))
    print("Number of test images:", len(test_paths))
    
    output_dir = Path(args.output)

    if not output_dir.is_dir():
        print(f"Could not find output dir ({output_dir}), creating one at specified location")
        output_dir.mkdir(parents=True)
    
    train_dir = output_dir.joinpath("train")
    val_dir = output_dir.joinpath("val")
    test_dir = output_dir.joinpath("test")
    
    train_output_paths = copy_paths(train_paths, train_dir, mode=args.mode)
    val_output_paths = copy_paths(val_paths, val_dir, mode=args.mode)
    test_output_paths = copy_paths(test_paths, test_dir, mode=args.mode)
    
    with open(output_dir.joinpath("filelist.txt"), mode='w') as f:
        for train_output_path in train_output_paths:
            f.write(f"{train_output_path.relative_to(output_dir)}\n")
        for val_output_path in val_output_paths:
            f.write(f"{val_output_path.relative_to(output_dir)}\n")
        for test_output_path in test_output_paths:
            f.write(f"{test_output_path.relative_to(output_dir)}\n")
            
    with open(output_dir.joinpath("info.txt"), mode='w') as f:
        f.write(f"Created: {datetime.now()}\n")
        f.write(f"Number of train images: {len(train_paths)}\n")
        f.write(f"Number of validation images: {len(val_paths)}\n")
        f.write(f"Number of test images: {len(test_paths)}\n")
        
    
if __name__ == "__main__":
    args = get_arguments()
    main(args)