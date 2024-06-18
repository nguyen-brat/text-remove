# Set environment
```bash
git clone https://github.com/nguyen-brat/text-remove.git
cd text-remove
conda create -n inpaint python==3.8
conda activate inpaint
sudo apt-get install libjpeg-dev zlib1g-dev
```

# Set up library
```bash
pip install torch==2.3.1
pip install torchvision==0.2.1
pip install opencv-python==4.10.0
pip install scikit-image==0.14.2
pip install tqdm==4.66.4
pip install yaml==6.0.1
pip install easydict
pip install scikit-learn==1.3.2
pip install pandas==2.0.3
pip install pytorch-lightning==2.3.0
pip install kornia==0.7.2
pip install hydra-core==1.1.0
pip install omegaconf==2.1.2
pip install albumentations==0.5.2
pip install webdataset==0.2.86
pip install pillow==6.1.0
```

# Set up Craft

```bash
cd CRAFT-pytorch
wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=1Jk4eGD7crsqCCg9C9VjCLkMN3ze8kutZ' -O "craft_mlt_25k.pth"
cd ..
```

# Set up lama
```bash
cd lama
curl -LJO https://huggingface.co/smartywu/big-lama/resolve/main/big-lama.zip
unzip big-lama.zip
cd ..
```

# text detection with craft and remove with lama
If you has large gpu you can enhance the result with refine feature you can go to lama/configs/prediction/default.yaml to change the number of gpu and run
```bash
bash config/test_detection_refine.sh -s path/to/the/folder/remove/text \
                                    -b path/to/the/bbox/folder \
                                    -t path/to/the/folder/saved/result
```
Else you can run only in cpu with no refine feature
```bash
bash config/text_detection.sh -s path/to/the/folder/remove/text \
                                -b path/to/the/bbox/folder \
                                -t path/to/the/folder/saved/result
```

# Example run with cpu
```bash
bash text_detection.sh -s test_folder -t target_test
```