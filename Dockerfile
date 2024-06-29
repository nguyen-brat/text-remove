# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    curl \
    ca-certificates \
    gcc \
    git \
    git-lfs \
    wget \
    libpq-dev \
    libsndfile1-dev \
    libgl1 \
    unzip \
    libjpeg-dev \
    libpng-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Create .streamlit/config.toml file
RUN mkdir -p /app/.streamlit && \
    echo "[server]\nenableXsrfProtection = false\nenableCORS = false" > /app/.streamlit/config.toml

# Clone the repository
RUN git clone https://github.com/nguyen-brat/text-remove.git /app/text-remove

# Set the working directory to the cloned repo
WORKDIR /app/text-remove

RUN mkdir -p /app/text-remove/.streamlit && \
    echo "[server]\nenableXsrfProtection = false\nenableCORS = false" > /app/text-remove/.streamlit/config.toml

# Install Python dependencies
COPY requirements.txt .
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

# Make port 7860 available to the world outside this container
EXPOSE 7860

# Run app.py when the container launches
ENTRYPOINT ["streamlit", "run"]
CMD ["app.py", "--server.port=7860"]
# CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]