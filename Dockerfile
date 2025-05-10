# Dockerfile for Music Source Separation Training (MSST)

# --------- STAGE: BUILD PYAUDIO ---------
FROM python:3.11-slim AS builder_pyaudio

# Install PyAudio build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Install wheel package (to build .whl files)
RUN pip install wheel

WORKDIR /wheels
# Build PyAudio wheel. This will fetch the latest compatible PyAudio.
# If you need a specific version, specify it e.g., "PyAudio==0.2.13"
RUN pip wheel --no-cache-dir PyAudio -w .






# Choose a base image with CUDA runtime compatible with PyTorch's cu126 index.
# Using CUDA 12.6.3 and Ubuntu 22.04 as a starting point.
# Adjust the CUDA version (e.g., 12.6.3) and PyTorch index (e.g., cu126)
# if your target Fargate instances use a different CUDA version.
FROM pytorch/pytorch:2.7.0-cuda12.6-cudnn9-runtime@sha256:27c3135420bc184e86977170b6158c6133be3c7cc5c35e9e4fa87bdda629dc2b

# Avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
RUN python3 --version && pip3 --version
# Install essential system packages, Python 3.11, pip, git, curl, MSST system dependencies, AND build tools
# TODO: split build-essential and python3.11-dev into elsewhere,
#       it build pyaudio but takes space.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    portaudio19-dev \
    ca-certificates \
    grep && \
    # Clean up apt cache
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3 -m pip install --no-cache-dir --upgrade pip


# Set the main working directory
WORKDIR /app

# Copy requirements files first to leverage Docker layer caching.
# Assumes this Dockerfile is at the repo root, and the submodule is checked out.
COPY requirements.txt ./
# Copy submodule requirements to a known location
COPY Music-Source-Separation-Training/requirements.txt ./submodule_requirements.txt

# Filter out wxpython from submodule requirements as done in the workflow
RUN grep -v '^wxpython==' ./submodule_requirements.txt > ./filtered_submodule_reqs.txt

# Copy PyAudio wheel from the builder stage
COPY --from=builder_pyaudio /wheels/pyaudio*.whl /tmp/
# Install the PyAudio wheel using the base image's python3 and pip
RUN python3 -m pip install --no-cache-dir /tmp/pyaudio*.whl && \
    rm /tmp/pyaudio*.whl
# Install Python dependencies from the main requirements and the filtered submodule requirements
RUN python3 -m pip install --no-cache-dir -r requirements.txt
RUN python3 -m pip install --no-cache-dir -r filtered_submodule_reqs.txt

# Copy the rest of the application code, including the submodule contents
COPY . /app

# Download and place the models into a specific directory within the image.
# This increases image size but makes runtime faster.
# Alternatively, download them from S3 in the entrypoint script.
RUN mkdir -p /app/models
RUN curl -L -o /app/models/model_bs_roformer_ep_368_sdr_12.9628.yaml https://raw.githubusercontent.com/TRvlvr/application_data/main/mdx_model_data/mdx_c_configs/model_bs_roformer_ep_368_sdr_12.9628.yaml && \
    curl -L -o /app/models/model_bs_roformer_ep_368_sdr_12.9628.ckpt https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/model_bs_roformer_ep_368_sdr_12.9628.ckpt

# Define default paths and model type using environment variables.
# These can be overridden by the Fargate Task Definition environment settings.
ENV MODEL_TYPE="bs_roformer"
ENV CONFIG_PATH="/app/models/model_bs_roformer_ep_368_sdr_12.9628.yaml"
ENV CHECKPOINT_PATH="/app/models/model_bs_roformer_ep_368_sdr_12.9628.ckpt"
# These INPUT/OUTPUT dirs are local paths within the container
ENV LOCAL_INPUT_DIR="/app/input"
ENV LOCAL_OUTPUT_DIR="/app/output"
# These S3 paths will be provided by the Lambda function triggering the task
ENV INPUT_S3_PREFIX=""
ENV OUTPUT_S3_PREFIX=""

# Create local directories for input/output processing
RUN mkdir -p $LOCAL_INPUT_DIR $LOCAL_OUTPUT_DIR

# Add an entrypoint script responsible for S3 sync and running the inference
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set the working directory for the inference script 
WORKDIR /app/Music-Source-Separation-Training

# Run the entrypoint script when the container starts
ENTRYPOINT ["/app/entrypoint.sh"]
