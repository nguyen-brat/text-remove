from PIL import Image, ImageDraw
import argparse
from glob import glob
import os
from os.path import join as osp
import warnings
import numpy as np

def draw_mask(origin, mask):
    # np_img = np.array(origin)
    # np_mask_img = np.array(mask)
    # bool_mask_img = (np_mask_img == 255)
    # np_img[bool_mask_img] = 255
    # pillow_image = Image.fromarray(np_img, 'RGB')
    rgb_array = np.array(origin)
    mask_array = np.array(mask)

    # Invert the mask (set 255 to 0 and vice versa) for element-wise multiplication
    inverted_mask = 255 - mask_array

    # Apply the mask using element-wise multiplication
    masked_rgb = rgb_array * inverted_mask[..., None]

    # Convert the masked array back to a PIL Image
    masked_image = Image.fromarray(masked_rgb.astype(np.uint8), mode='RGB')

    return masked_image

def main(args):
    image_paths, bbox_file_paths, save_path = args.src_img_path, args.bbox_img_path, args.save_img_path
    os.makedirs(save_path, exist_ok=True)
    # Open the image
    image_paths = glob(image_paths + "/*")
    for i, image_path in enumerate(image_paths):
        image_name = image_path.split("/")[-1].split(".")[0]
        bbox_file_name = "res_" + image_path.split("/")[-1].split(".")[0] + ".txt"
        bbox_file_path = osp(bbox_file_paths, bbox_file_name)
        image = Image.open(image_path)
        masked_image = Image.new('L', image.size, 0)  # Create a new image for the mask

        # Create a drawing context for the mask
        draw = ImageDraw.Draw(masked_image)
        #draw_merge = ImageDraw.Draw(image)
        # Read the bounding boxes from the text file
        with open(bbox_file_path, 'r') as file:
            for line in file:
                # Each line should contain eight coordinates: x1, y1, x2, y2, x3, y3, x4, y4
                coordinates = list(map(int, line.strip().split(',')))
                if len(coordinates) != 8:
                    raise warnings.warn("Each line must contain exactly 8 integers")
                polygon = [(coordinates[i], coordinates[i+1]) for i in range(0, len(coordinates), 2)]
                # Draw the polygon for the mask
                draw.polygon(polygon, fill=255)
                #draw_merge.polygon(polygon, fill=0)
        #image = draw_mask(image, masked_image)
        image_mask_saved_name = image_name + f"_mask{i:03d}.png"
        image_saved_name = image_name + ".png"
        masked_image.save(osp(save_path, image_mask_saved_name))
        image.save(osp(save_path, image_saved_name))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments for fact verify Trainning")
    parser.add_argument("--src_img_path", type=str, help="folder path of image need to detect text")
    parser.add_argument("--bbox_img_path", default="CRAFT-pytorch/result", type=str, help="folder path of bbox image")
    parser.add_argument("--save_img_path", type=str, help="folder path of bbox image")
    args = parser.parse_args()
    main(args=args)
    # bash config/text_detection.sh -s test_folder -t target_test