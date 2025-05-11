#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Starting MSST Fargate Task..."
echo "Input S3 Prefix: ${INPUT_S3_PREFIX}"
echo "Output S3 Prefix: ${OUTPUT_S3_PREFIX}"
echo "Local Input Dir: ${LOCAL_INPUT_DIR}"
echo "Local Output Dir: ${LOCAL_OUTPUT_DIR}"

# Ensure local directories exist (though Dockerfile should create them)
mkdir -p "${LOCAL_INPUT_DIR}"
mkdir -p "${LOCAL_OUTPUT_DIR}"

# Sync input files from S3 to the local input directory
echo "Downloading input files from ${INPUT_S3_PREFIX}..."
aws s3 sync "${INPUT_S3_PREFIX}" "${LOCAL_INPUT_DIR}"

# Check if input files were downloaded
if [ -z "$(ls -A ${LOCAL_INPUT_DIR})" ]; then
   echo "Error: No input files found after syncing from ${INPUT_S3_PREFIX}"
   exit 1
fi

echo "Running inference..."
# Call the inference script using the environment variables for configuration.
# -u: force unbuffered binary stdout and stderr
# 2>&1: redirect stderr of python script to its stdout
# The pipe sends this combined stream to tee.
# tee does two things:
#   1. Writes the raw stream to "${LOCAL_OUTPUT_DIR}/inference_run.log"
#   2. Writes the raw stream to the process substitution >(tr '\r' '\n')
#      The process substitution runs 'tr', which converts '\r' to '\n'.
#      The output of 'tr' (processed stream) goes to the main stdout of this pipeline,
#      which is then captured by CloudWatch.

python3 -u inference.py \
    --model_type "${MODEL_TYPE}" \
    --config_path "${CONFIG_PATH}" \
    --start_check_point "${CHECKPOINT_PATH}" \
    --input_folder "${LOCAL_INPUT_DIR}" \
    --store_dir "${LOCAL_OUTPUT_DIR}" \
    2>&1 | tee "${LOCAL_OUTPUT_DIR}/inference_run.log" >(tr '\r' '\n')

echo "Inference complete." # This will appear in CloudWatch after python script finishes.

# Sync results from the local output directory back to S3
# This will include the raw inference_run.log file
echo "Uploading results to ${OUTPUT_S3_PREFIX}..."
aws s3 sync "${LOCAL_OUTPUT_DIR}" "${OUTPUT_S3_PREFIX}"

echo "Upload complete. Task finished successfully."

# Optional: Add cleanup of local directories if needed
# rm -rf "${LOCAL_INPUT_DIR}"/*
# rm -rf "${LOCAL_OUTPUT_DIR}"/*

# Optional: Add notification logic here (e.g., send SQS message)
# aws sqs send-message --queue-url <your-queue-url> --message-body '{"jobId": "'"$JOB_ID"'", "status": "success"}'

exit 0
