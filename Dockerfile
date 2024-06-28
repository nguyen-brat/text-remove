# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app
# Install system dependencies
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    curl \
    unzip \
    wget \
    git

# Clone the repository
RUN git clone https://github.com/nguyen-brat/text-remove.git .
WORKDIR /app/text-remove
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set up Craft
WORKDIR /app/text-remove/CRAFT-pytorch
RUN wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=1Jk4eGD7crsqCCg9C9VjCLkMN3ze8kutZ' -O "craft_mlt_25k.pth"
RUN pip install gdown
RUN gdown 1XSaFwBkOaFOdtk4Ane3DFyJGPRw6v5bO

# Set up lama
WORKDIR /app/text-remove/lama
RUN curl -LJO https://huggingface.co/smartywu/big-lama/resolve/main/big-lama.zip
RUN unzip big-lama.zip

# Set the working directory back to the root of the project
WORKDIR /app/text-remove

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Run app.py when the container launches
CMD ["streamlit", "run", "app.py"]