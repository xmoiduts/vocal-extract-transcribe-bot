#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Container starting..."
echo "CLOUD_PLATFORM environment variable is: '${CLOUD_PLATFORM}'"

# Determine the cloud platform and execute platform-specific logic
if [ "$CLOUD_PLATFORM" == "RUNPOD" ]; then
    echo "RUNPOD mode detected. Executing RunPod Python handler..."
    # Ensure the runpod_adapter directory and handler.py are in the correct path
    # The python3 executable should be the one configured in the Dockerfile (python3.11)
    # exec will replace the shell process with the python process.
    exec python3 /app/runpod_adapter/handler.py

elif [ "$CLOUD_PLATFORM" == "AWS" ] || [ -z "$CLOUD_PLATFORM" ]; then
    # Default to AWS Container Service (Fargate/ECS) behavior if CLOUD_PLATFORM is "AWS" or not set/empty
    if [ -z "$CLOUD_PLATFORM" ]; then
        echo "CLOUD_PLATFORM not set, defaulting to AWS Container Service (Fargate/ECS) mode."
    else
        echo "AWS Container Service (Fargate/ECS) mode detected."
    fi

    echo "Starting MSST AWS Task..."
    # These ENV VARS are expected to be set by the AWS Task Definition
    echo "Input S3 Prefix: ${INPUT_S3_PREFIX}"
    echo "Output S3 Prefix: ${OUTPUT_S3_PREFIX}"
    echo "Local Input Dir: ${LOCAL_INPUT_DIR}"
    echo "Local Output Dir: ${LOCAL_OUTPUT_DIR}"
    echo "Model Type: ${MODEL_TYPE}"
    echo "Config Path: ${CONFIG_PATH}"
    echo "Checkpoint Path: ${CHECKPOINT_PATH}"

    # Validate required environment variables for AWS mode
    if [ -z "$INPUT_S3_PREFIX" ] || [ -z "$OUTPUT_S3_PREFIX" ] || \
       [ -z "$LOCAL_INPUT_DIR" ] || [ -z "$LOCAL_OUTPUT_DIR" ] || \
       [ -z "$MODEL_TYPE" ] || [ -z "$CONFIG_PATH" ] || [ -z "$CHECKPOINT_PATH" ]; then
        echo "Error: One or more required environment variables for AWS mode are not set."
        echo "Required: INPUT_S3_PREFIX, OUTPUT_S3_PREFIX, LOCAL_INPUT_DIR, LOCAL_OUTPUT_DIR, MODEL_TYPE, CONFIG_PATH, CHECKPOINT_PATH"
        exit 1
    fi

    # Ensure local directories exist (though Dockerfile should create them)
    # Clean them first for a fresh run, similar to the RunPod handler.
    echo "Cleaning and creating local directories..."
    rm -rf "${LOCAL_INPUT_DIR:?}"/* || true # Protect against empty var and ignore errors if dir is empty/not found
    rm -rf "${LOCAL_OUTPUT_DIR:?}"/* || true
    mkdir -p "${LOCAL_INPUT_DIR}"
    mkdir -p "${LOCAL_OUTPUT_DIR}"

    # Sync input files from S3 to the local input directory
    echo "Downloading input files from ${INPUT_S3_PREFIX} (verbose)..."
    aws s3 sync "${INPUT_S3_PREFIX}" "${LOCAL_INPUT_DIR}" # Removed --quiet

    # Check if input files were downloaded
    if [ -z "$(ls -A ${LOCAL_INPUT_DIR})" ]; then
       echo "Error: No input files found after syncing from ${INPUT_S3_PREFIX}"
       # Attempt to upload a log file indicating this failure
       echo "Error: No input files found after syncing from ${INPUT_S3_PREFIX}" > "${LOCAL_OUTPUT_DIR}/aws_task_error.log"
       aws s3 sync "${LOCAL_OUTPUT_DIR}" "${OUTPUT_S3_PREFIX}" || echo "Failed to upload error log." # Removed --quiet
       exit 1
    fi
    echo "Input files downloaded."

    echo "Running inference..."
    # Using full path for clarity
    INFERENCE_LOG_FILE="${LOCAL_OUTPUT_DIR}/inference_run.log"
    
    python3 -u /app/Music-Source-Separation-Training/inference.py \
        --model_type "${MODEL_TYPE}" \
        --config_path "${CONFIG_PATH}" \
        --start_check_point "${CHECKPOINT_PATH}" \
        --input_folder "${LOCAL_INPUT_DIR}" \
        --store_dir "${LOCAL_OUTPUT_DIR}" \
        2>&1 | tee "${INFERENCE_LOG_FILE}" | tr '\r' '\n'
    
    if [ "${PIPESTATUS[0]}" -ne 0 ]; then
        echo "Error: Inference script failed with exit code ${PIPESTATUS[0]}."
        echo "Uploading failed inference logs and any partial output to ${OUTPUT_S3_PREFIX} (verbose)..."
        aws s3 sync "${LOCAL_OUTPUT_DIR}" "${OUTPUT_S3_PREFIX}" || echo "Failed to upload error logs/output." # Removed --quiet
        exit 1 
    fi
    echo "Inference complete."

    # Post-process local output directory (TBD Placeholder)
    # =====================================================================
    # TODO: Implement post-processing of files in LOCAL_OUTPUT_DIR if needed.
    # Example:
    # if [ -f "/app/scripts/post_process.sh" ]; then
    #    echo "Running post_processing script..."
    #    /app/scripts/post_process.sh "${LOCAL_OUTPUT_DIR}"
    #    if [ $? -ne 0 ]; then
    #        echo "Error: Post-processing script failed."
    #        aws s3 sync "${LOCAL_OUTPUT_DIR}" "${OUTPUT_S3_PREFIX}" || echo "Failed to upload logs after post-process failure." # Removed --quiet
    #        exit 1
    #    fi
    # fi
    # =====================================================================
    echo "Post-processing step (if any) skipped/completed."

    # Sync results from the local output directory back to S3
    echo "Uploading results to ${OUTPUT_S3_PREFIX} (verbose)..."
    aws s3 sync "${LOCAL_OUTPUT_DIR}" "${OUTPUT_S3_PREFIX}" # Removed --quiet
    if [ $? -ne 0 ]; then
        echo "Error: Failed to upload results to ${OUTPUT_S3_PREFIX}."
        exit 1
    fi

    echo "Upload complete. AWS Container Service Task finished successfully."

else
    echo "Error: Unknown CLOUD_PLATFORM value: '${CLOUD_PLATFORM}'"
    echo "Supported values are 'RUNPOD' or 'AWS' (or leave empty for AWS default)."
    exit 1
fi

exit 0
