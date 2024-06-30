#!/bin/bash

# Define variables to store arguments and flags
root=$(pwd)
src_path=""
save_path=""

# Process flags and arguments using a loop
while getopts ":s:b:t:" opt; do
  case $opt in
    s) src_path="$OPTARG";;
    t) save_path="$OPTARG";;
    \?) echo "Invalid option: -$OPTARG" >&2; exit 1;;
  esac
done

# Shift arguments to remove flags
shift $((OPTIND-1))

# Check if arguments are provided
if [[ -z "$src_path" || -z "$save_path" ]]; then
  echo "Usage: $0 Must declare -s src_path and -t target path flag" >&2
  exit 1
fi

cd craft_pytorch
PYTHONPATH=. TORCH_HOME=$(pwd)/craft_pytorch python3 test.py --trained_model=craft_mlt_25k.pth \
                                                              --refiner_model=craft_refiner_CTW1500.pth \
                                                              --test_folder="$src_path" \
                                                              --bbox_folder="$save_path/bbox" \
                                                              --cuda False

cd ..
PYTHONPATH=$(pwd) python3 draw_bb.py --src_img_path $src_path \
                                                  --bbox_img_path $save_path/bbox \
                                                  --save_img_path $save_path/mask

cd lama
export TORCH_HOME=$(pwd) && export PYTHONPATH=$(pwd)
python3 ./bin/predict.py refine=True model.path=$(pwd)/big-lama \
                          indir=$save_path/mask \
                          outdir=$save_path/result \
                          dataset.img_suffix=.png > /dev/null