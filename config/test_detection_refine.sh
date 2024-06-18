#!/bin/bash

# Define variables to store arguments and flags
root=$(pwd)
src_path=""
bbox_path="CRAFT-pytorch/result"
save_path=""

# Process flags and arguments using a loop
while getopts ":s:b:t:" opt; do
  case $opt in
    s) src_path="$OPTARG";; 
    b) bbox_path="$OPTARG";;
    t) save_path="$OPTARG";;
    \?) echo "Invalid option: -$OPTARG" >&2; exit 1;;
  esac
done

# Shift arguments to remove flags
shift $((OPTIND-1))

# Check if arguments are provided
if [[ -z "$src_path" || -z "$bbox_path" || -z "$save_path" ]]; then
  echo "Usage: $0 Must declare -s src_path and -t target path flag" >&2
  exit 1
fi

cd CRAFT-pytorch
PYTHONPATH=. TORCH_HOME=$(pwd)/CRAFT-pytorch python3 test.py --trained_model=craft_mlt_25k.pth \
                                                              --test_folder="../$src_path" \
                                                              --cuda True

cd ..
PYTHONPATH=$(pwd) python3 draw_bb.py --src_img_path $src_path \
                                                  --bbox_img_path $bbox_path \
                                                  --save_img_path $save_path/mask

cd lama
export TORCH_HOME=$(pwd) && export PYTHONPATH=$(pwd)
python3 ./bin/predict.py refine=True model.path=$(pwd)/big-lama \
                          indir=$root/$save_path/mask \
                          outdir=$root/$save_path/result \
                          dataset.img_suffix=.png > /dev/null