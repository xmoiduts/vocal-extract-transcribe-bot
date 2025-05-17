# vocal-extract-transcribe-bot
extract vocal stem of musics then transcribe and format with external big model API's

Performance comparison per page: [performance-comparison.md](performance-comparison.md)


# deploy
## Environment Variables:
### Common:
Optional: (Preconfigured in Dockerfile)
- LOCAL_OUTPUT_DIR
- LOCAL_INPUT_DIR
- MODEL_TYPE
- CONFIG_PATH
- CHECKPOINT_PATH
- CLOUD_PLATFORM (Default to AWS)
### AWS
- CLOUD_PLATFORM: AWS
- OUTPUT_S3_PREFIX
- INPUT_S3_PREFIX
### RunPod
- CLOUD_PLATFORM: RUNPOD
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_DEFAULT_REGION
    - (Recommended) The AWS region your S3 buckets are in (e.g., us-east-1). While not strictly for authentication, it's often needed for the CLI to function correctly.
