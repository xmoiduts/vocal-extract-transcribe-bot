# Dockerfile for Music Source Separation Training (MSST)

# ---------------------------------------------------------------------
# ----------------- STAGE: BUILD PYTHON DEPENDENCIES ------------------
# ---------------------------------------------------------------------
FROM nvidia/cuda:12.6.3-base-ubuntu22.04 AS builder_submodule_wheels

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    portaudio19-dev \
    ca-certificates \
    grep \
    # Add Python for the builder stage
    python3.11 \ 
    # python3.11-dev should bring python3.11-pip or ensure pip works for 3.11
    python3.11-dev \
    # General pip3, to be sure
    python3-pip && \ 
    # Make python3.11 the default python3
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    # Ensure pip is linked to the new default python3
    # This is often handled by python3-pip installation and update-alternatives for python3
    # Or by directly using python3 -m pip
    # Clean up apt cache
    rm -rf /var/lib/apt/lists/*

# Now python3 should be python3.11. Use it to upgrade pip and install wheel.
RUN python3 -m pip install --upgrade pip wheel
WORKDIR /app_build

# Copy requirements files
COPY requirements.txt ./main_requirements.txt
COPY Music-Source-Separation-Training/requirements.txt ./submodule_requirements.txt

# Filter out wxpython, torch, and torchaudio from submodule requirements
# We exclude torch and torchaudio because they're already downloaded with CUDA support
RUN grep -v -E '^(wxpython==|torch>=|torch==|torchaudio$|torchaudio==|torchaudio>=)' ./submodule_requirements.txt > ./filtered_submodule_reqs.txt

# Combine and deduplicate requirements files, then display them
RUN cat ./main_requirements.txt ./filtered_submodule_reqs.txt | sort -u > ./all_requirements.txt && \
    echo "--- Combined requirements START ---" && \
    cat ./all_requirements.txt && \
    echo "--- Combined requirements END ---"

# Copy and prepare the wheel partitioning script
COPY scripts/partition_wheels.py .
RUN chmod +x ./partition_wheels.py

# Explicitly use python3 (which now should be python3.11) for building wheels
# Specify to use CUDA torch upfront
RUN python3 -m pip wheel --no-cache-dir \
        --extra-index-url https://download.pytorch.org/whl/cu126 \
        torch torchaudio \
        -w /all_wheels && \
        echo "Pip cache cleanup [torch]: Removing /root/.cache/pip" && \
        rm -rf /root/.cache/pip

# Download other requirements
RUN python3 -m pip wheel --no-cache-dir \
        -r ./all_requirements.txt \
        -w /all_wheels && \
    echo "Pip cache cleanup [MSST]: Removing /root/.cache/pip" && \
    rm -rf /root/.cache/pip

# Display total size of all wheels and partition them
RUN echo "Total size of all wheels:" && du -sh /all_wheels && \
    ./partition_wheels.py /all_wheels 6

# ---------------------------------------------------------------------
# ------------------------- STAGE: FINAL IMAGE ------------------------
# ---------------------------------------------------------------------

# Choose a base image with CUDA runtime compatible with PyTorch's cu129 index.
# Using CUDA 12.9.0 and Ubuntu 22.04 as a starting point.
# Adjust the CUDA version (e.g., 12.9.0) and PyTorch index (e.g., cu129)
# if your target Fargate instances use a different CUDA version.
FROM nvidia/cuda:12.6.3-base-ubuntu22.04

# Avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Python for the final stage
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3.11 \
    python3-pip &&\
    #python3.11-dev && \ # for triton that we decided to not use as lowering performance
    # Make python3.11 the default python3
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    rm -rf /var/lib/apt/lists/*

RUN python3 --version && python3 -m pip --version
# Install essential system packages, Python 3.11, pip, git, curl, MSST system dependencies, AND build tools
# TODO: split build-essential and python3.11-dev into elsewhere,
#       it build pyaudio but takes space.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    # Runtime libraries for pyaudio
    libportaudio2 \
    # Needed for HTTPS connections (e.g. by curl)
    ca-certificates \
    # C compiler needed by triton for runtime compilation
    #gcc \
    # C standard library development files (e.g. stdlib.h), needed by triton
    #libc6-dev \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Download the large, static model checkpoint first to leverage caching.
# This layer is large but should rarely change.
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    mkdir -p /app/models && \
    echo "Downloading large model checkpoint..." && \
    curl -L -o /app/models/model_bs_roformer_ep_368_sdr_12.9628.ckpt https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/model_bs_roformer_ep_368_sdr_12.9628.ckpt && \
    apt-get purge -y --auto-remove curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Download the model config, modify it, and clean up.
# This layer is small and may change if the config URL or patch logic changes.
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl sed && \
    echo "Downloading and patching model config..." && \
    curl -L -o /app/models/model_bs_roformer_ep_368_sdr_12.9628.yaml https://raw.githubusercontent.com/TRvlvr/application_data/main/mdx_model_data/mdx_c_configs/model_bs_roformer_ep_368_sdr_12.9628.yaml && \
    # Sage Attention is Linux-only, windows use `triton-windows` 3rd party package.
    # It ~~boosts some~~ drags performance.
    # ~~As it is added to the MSST engine later, earlier models need to have this manually hacked in~~.
    # echo "Enabling 'sage_attention' and disabling 'flash_attn' in model config" && \
    # sed -i \
    #     -e '/^model:/a \ \ sage_attention: True' \
    #     -e 's/flash_attn: true/flash_attn: false/' \
    #     /app/models/model_bs_roformer_ep_368_sdr_12.9628.yaml && \
    # keep sed, attempting to remove it will break the build.
    apt-get purge -y --auto-remove curl && \
    apt-get clean && \
    # Clean up apt cache
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3 -m pip install --no-cache-dir --upgrade pip

# Set the main working directory
WORKDIR /app

# python dependencies
COPY --from=builder_submodule_wheels /app_build/part_*_wheels.txt ./

# Install dependencies in partitioned layers to optimize pull times
# Each RUN command creates a new layer.
# Use mount to avoid [copying] the large all_wheels directory (3-6 GB) 
# which cannot be later deleted.
RUN --mount=type=bind,from=builder_submodule_wheels,source=/all_wheels,target=/all_wheels \
    xargs -a part_1_wheels.txt python3 -m pip install --no-cache-dir --no-deps

RUN --mount=type=bind,from=builder_submodule_wheels,source=/all_wheels,target=/all_wheels \
    xargs -a part_2_wheels.txt python3 -m pip install --no-cache-dir --no-deps

RUN --mount=type=bind,from=builder_submodule_wheels,source=/all_wheels,target=/all_wheels \
    xargs -a part_3_wheels.txt python3 -m pip install --no-cache-dir --no-deps

RUN --mount=type=bind,from=builder_submodule_wheels,source=/all_wheels,target=/all_wheels \
    xargs -a part_4_wheels.txt python3 -m pip install --no-cache-dir --no-deps

# Copy the rest of the application code, including the submodule contents
COPY ./Music-Source-Separation-Training /app/Music-Source-Separation-Training

# 再复制其他可能经常变动的文件或目录
#COPY ./bot-src /app/bot-src
COPY ./runpod_adapter /app/runpod_adapter
#COPY ./other_specific_file_or_dir /app/other_specific_file_or_dir
COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

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


# Set the working directory for the inference script 
WORKDIR /app/Music-Source-Separation-Training

# Run the entrypoint script when the container starts
ENTRYPOINT ["/app/entrypoint.sh"]
