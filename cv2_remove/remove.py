import sys
import os
import time
import argparse
from PIL import Image
import cv2
from skimage import io
import numpy as np
from glob import glob
import json
import zipfile
import matplotlib.pyplot as plt


def parse_args():
    parser = argparse.ArgumentParser(description='cv2 inpaint config')
    parser.add_argument('--output_path', default="target_test", type=str, help='pretrained refiner model')
    parser.add_argument('--input_path', default="test_folder", type=str, help='pretrained refiner model')
    args = parser.parse_args()

    return args

def main(args):
    input_path = args.input_path
    output_path = args.output_path
    img_paths = glob(f'{input_path}/*')
    for img_path in img_paths:
        img_name = img_path.split('/')[-1].split('.')[0]
        raw_img = cv2.imread(img_path)
        mask_img_path = glob(f'{output_path}/mask/{img_name}_mask*.png')[0]
        mask_img = cv2.imread(mask_img_path, cv2.COLOR_GRAY2BGR)
        telea_inpaint = cv2.inpaint(raw_img, mask_img, 3, cv2.INPAINT_TELEA)
        cv2.imwrite(f'{output_path}/result/{img_name}.png', telea_inpaint)


if __name__ == "__main__":
    args = parse_args()
    main(args=args)