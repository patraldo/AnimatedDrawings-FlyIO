# Use stable Debian Bookworm base for compatibility
FROM python:3.9-slim-bookworm

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Install system dependencies
# Required for headless OpenGL (Mesa), video encoding (ffmpeg), and model downloads
RUN apt-get update && \
    apt-get install -y \
        ffmpeg \
        curl \
        wget \
        unzip \
        libgl1-mesa-glx \
        libgl1-mesa-dri \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Use CPU-only PyTorch from official index
RUN pip install --no-cache-dir \
    torch==2.1.0 \
    torchvision==0.16.0 \
    torchaudio==2.1.0 \
    --index-url https://download.pytorch.org/whl/cpu

# Install application dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    python-multipart \
    requests \
    imageio \
    imageio-ffmpeg \
    matplotlib \
    scikit-image \
    tqdm \
    numpy \
    pillow

# Install gdown for reliable Google Drive downloads
RUN pip install --no-cache-dir gdown

# Create models directory
RUN mkdir -p models

# Download hub_checkpoints.zip from Google Drive
# Replace the ID with your actual file ID
RUN gdown "https://drive.google.com/uc?id=1CzZ1Ljj6wLO_zJEIVmuklBxN7TxkTsGE" -O models/hub_checkpoints.zip && \
    unzip -q models/hub_checkpoints.zip -d models/ && \
    rm models/hub_checkpoints.zip

# Download motion_generators.zip from Google Drive
# Replace YOUR_MOTION_ID with your actual file ID
RUN gdown "https://drive.google.com/uc?id=12v6FPZE0gUn:qiQlBT9xU71ADQTqIEq7G7" -O models/motion_generators.zip && \
    unzip -q models/motion_generators.zip -d models/ && \
    rm models/motion_generators.zip

# Expose port
EXPOSE 8000

# Run the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
