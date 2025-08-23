# torchserve/Dockerfile
FROM python:3.8.13-slim

# Disable GPU
ENV CUDA_VISIBLE_DEVICES=""
# Set OpenGL platform to OSMesa (for headless rendering)
ENV PYOPENGL_PLATFORM=osmesa
ENV MESA_GL_VERSION_OVERRIDE=3.3

# Install system deps (critical for cv2 + OSMesa)
RUN apt-get update && \
    apt-get install -y \
        curl \
        unzip \
        default-jre-headless \
        git \
        net-tools \
        procps \
        ffmpeg \
        # For cv2
        libgl1-mesa-glx \
        libgl1-mesa-dri \
        libglx-mesa0 \
        libegl-mesa0 \
        libgbm1 \
        # For OSMesa (headless OpenGL)
        libosmesa6 \
        libosmesa6-dev \
        # For GUI deps (optional but safe)
        libsm6 \
        libxrender1 \
        libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /home/model-server

# Copy code
COPY animated_drawings/ /home/model-server/animated_drawings/
COPY animated_drawings/mvc_base_cfg.yaml /home/model-server/mvc_base_cfg.yaml
# Copy example scripts
COPY examples/ /home/model-server/examples/

# Copy drawings
COPY examples/drawings/ /home/model-server/drawings/

# Add to Python path
ENV PYTHONPATH=/home/model-server:${PYTHONPATH}

# Create model store
RUN mkdir -p /home/torchserve/model-store

# Download .mar files
RUN curl -L -f -o /home/torchserve/model-store/drawn_humanoid_detector.mar \
    "https://github.com/facebookresearch/AnimatedDrawings/releases/download/v0.0.1/drawn_humanoid_detector.mar"

RUN curl -L -f -o /home/torchserve/model-store/drawn_humanoid_pose_estimator.mar \
    "https://github.com/facebookresearch/AnimatedDrawings/releases/download/v0.0.1/drawn_humanoid_pose_estimator.mar"

# Fix xtcocoapi (required by mmpose)
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential python3-dev && \
    git clone https://github.com/jin-s13/xtcocoapi.git && \
    cd xtcocoapi && \
    pip install --no-cache-dir -r requirements.txt && \
    python setup.py build_ext install && \
    cd .. && \
    rm -rf xtcocoapi && \
    apt-get remove -y build-essential python3-dev && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Install PyTorch 1.13.0 (required for mmcv-full==1.7.0)
RUN pip install --no-cache-dir torch==1.13.0 --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir torchvision==0.14.0 --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir torchaudio==0.13.0 --index-url https://download.pytorch.org/whl/cpu

# Install torchserve
RUN pip install --no-cache-dir torchserve torch-model-archiver

# Install OpenMMLab dependencies
RUN pip install --no-cache-dir mmdet==2.27.0
RUN pip install --no-cache-dir mmpose==0.29.0
RUN pip install --no-cache-dir numpy==1.24.4
RUN pip install --no-cache-dir pyyaml==6.0
RUN pip install --no-cache-dir opencv-python-headless==4.8.0.74
RUN pip install --no-cache-dir PyOpenGL==3.1.6
RUN pip install --no-cache-dir scikit-image==0.19.3

# Install optional but required dependencies with version pins
RUN pip install --no-cache-dir \
    shapely==1.8.5 \
    scikit-image==0.19.3 \
    scikit-learn==1.2.2 \
    matplotlib==3.7.5 \
    yapf==0.40.2 \
    isort==5.13.2 \
    pycocotools==2.0.7 \
    tqdm==4.66.1

# Install mmcv-full 1.7.0 (after mmpose, so it wins)
RUN pip install "https://download.openmmlab.com/mmcv/dist/cpu/torch1.13.0/mmcv_full-1.7.0-cp38-cp38-manylinux1_x86_64.whl" \
    --trusted-host download.openmmlab.com

# Copy config
COPY torchserve/config.properties /home/torchserve/config.properties

# Extract handlers
RUN mkdir -p /tmp/mar && \
    unzip /home/torchserve/model-store/drawn_humanoid_detector.mar -d /tmp/mar && \
    mkdir -p /usr/local/lib/python3.8/site-packages/ts/torch_handler && \
    cp /tmp/mar/mmdet_handler.py /usr/local/lib/python3.8/site-packages/ts/torch_handler/mmdet_handler.py

RUN mkdir -p /tmp/pose_mar && \
    unzip /home/torchserve/model-store/drawn_humanoid_pose_estimator.mar -d /tmp/pose_mar && \
    cp /tmp/pose_mar/mmpose_handler.py /usr/local/lib/python3.8/site-packages/ts/torch_handler/mmpose_handler.py

# Start TorchServe
CMD ["sh", "-c", "mkdir -p /data/uploads /data/output /data/logs && torchserve --start --disable-token-auth --ts-config /home/torchserve/config.properties --foreground"]
