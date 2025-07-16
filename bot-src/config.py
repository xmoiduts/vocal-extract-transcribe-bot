import os
from typing import Optional


class BotConfig:
    """Bot配置管理"""
    
    def __init__(self):
        # Bot基本配置
        self.bot_token: Optional[str] = os.getenv('TELEGRAM_BOT_TOKEN')
        self.bot_username: str = os.getenv('TELEGRAM_BOT_USERNAME') # TODO: do we really need TG username?
        
        # API配置
        self.telegram_api_base = "https://api.telegram.org"
        
        # AWS配置
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        self.dynamodb_table_prefix = os.getenv('DYNAMODB_TABLE_PREFIX', 'transcribe-bot')
        #self.s3_bucket_name = os.getenv('S3_BUCKET_NAME', 'vocal-transcribe-files') # not yet used
        
        # 消息配置
        """ # not yet used
        self.max_file_size_mb = 50  # 最大文件大小限制（MB）
        self.supported_languages = ['en', 'zh']
        self.default_language = 'en'
        """
        # 转录配置
        """ # not yet used, should move to config.yaml
        self.whisper_model = 'large-v3' # try gemini-2.5-pro native
        self.max_duration_minutes = 60  # 最大音频时长限制（分钟） 
        """

    def get_bot_mention(self) -> str:
        """获取bot的@提及格式"""
        return f"@{self.bot_username}"
    
    def is_command_for_this_bot(self, command: str) -> bool:
        """检查命令是否是针对当前bot的"""
        if '@' not in command:
            return True  # 私聊中的命令默认是给bot的
        
        # 提取@后面的bot用户名
        parts = command.split('@')
        if len(parts) == 2:
            mentioned_bot = parts[1].lower()
            return mentioned_bot == self.bot_username.lower()
        
        return False
    
    def validate_config(self) -> bool:
        """验证配置是否完整"""
        if not self.bot_token:
            print("❌ Error: TELEGRAM_BOT_TOKEN environment variable is required")
            return False
        
        if not self.bot_username:
            print("❌ Error: TELEGRAM_BOT_USERNAME is required")
            return False
            
        return True


# 全局配置实例
config = BotConfig() 