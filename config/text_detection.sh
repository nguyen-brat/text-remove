#!/bin/bash

# Define variables to store arguments and flags
root=$(pwd)
src_path=""
bbox_path="craft_pytorch/result"
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

cd craft_pytorch
if [ ! -f "craft_mlt_25k.pth" ]; then
    echo "craft_mlt_25k.pth does not exist. Downloading..."
    wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=1Jk4eGD7crsqCCg9C9VjCLkMN3ze8kutZ' -O "craft_mlt_25k.pth"
fi
if [ ! -f "craft_refiner_CTW1500.pth" ]; then
    echo "craft_refiner_CTW1500.pth does not exist. Downloading..."
    gdown 1XSaFwBkOaFOdtk4Ane3DFyJGPRw6v5bO
fi
PYTHONPATH=. TORCH_HOME=$(pwd)/craft_pytorch python3 test.py --trained_model=craft_mlt_25k.pth \
                                                              --refiner_model=craft_refiner_CTW1500.pth \
                                                              --test_folder="../$src_path" \
                                                              --cuda False

cd ..
PYTHONPATH=$(pwd) python3 draw_bb.py --src_img_path $src_path \
                                                  --bbox_img_path $bbox_path \
                                                  --save_img_path $save_path/mask

cd lama
if [ ! -d "big-lama" ]; then
    echo "big-lama does not exist. Downloading..."
    curl -LJO https://huggingface.co/smartywu/big-lama/resolve/main/big-lama.zip
    unzip big-lama.zip
    rm big-lama.zip
fi
export TORCH_HOME=$(pwd) && export PYTHONPATH=$(pwd)
python3 ./bin/predict.py refine=True model.path=$(pwd)/big-lama \
                          indir=$root/$save_path/mask \
                          outdir=$root/$save_path/result \
                          dataset.img_suffix=.png > /dev/null

rm -r ../$save_path/mask/*