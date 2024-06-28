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
pip install -r requirements.txt
```

# Set up Craft

```bash
cd CRAFT-pytorch
wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=1Jk4eGD7crsqCCg9C9VjCLkMN3ze8kutZ' -O "craft_mlt_25k.pth"
gdown 1XSaFwBkOaFOdtk4Ane3DFyJGPRw6v5bO
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
                                    -t path/to/the/folder/saved/result
```
Else you can run only in cpu with no refine feature
```bash
bash config/text_detection.sh -s path/to/the/folder/remove/text \
                                -t path/to/the/folder/saved/result
```

# Example run with cpu
```bash
bash config/text_detection.sh -s test_folder -t target_test
```