# vocal-extract-transcribe-bot
extract vocal stem of musics then transcribe and format with external big model API's

Performance comparison per page: [performance-comparison.md](performance-comparison.md)


# deploy
## Environment Variables:
### Cloud environment variables common:
- LOCAL_OUTPUT_DIR
- LOCAL_INPUT_DIR
- MODEL_TYPE
- CONFIG_PATH
- CHECKPOINT_PATH
- CLOUD_PLATFORM (Default to AWS)
### AWS specific:
- CLOUD_PLATFORM: AWS
- OUTPUT_S3_PREFIX
- INPUT_S3_PREFIX
### RunPod specific:
- CLOUD_PLATFORM: RUNPOD
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_DEFAULT_REGION
    - (Recommended) The AWS region your S3 buckets are in (e.g., us-east-1). While not strictly for authentication, it's often needed for the CLI to function correctly.

## TG-specific:
- `Privacy mode` must be turned **off** for the bot to properly receive messages
- TELEGRAM_BOT_TOKEN (AWS lambda, GitHub Actions)
- TELEGRAM_BOT_USERNAME
- TELEGRAM_WEBHOOK_URL # use lambda service
- configured bot quick function commands like `/transcribe` and `/add_music@<bot_username>`




