#!/usr/bin/env python3
"""
数据库设置脚本
用于初始化DynamoDB表格和执行基本的数据库操作测试
"""

import os
import sys
import argparse
from db_init import DynamoDBInitializer
from database import DatabaseManager
from config import config


def setup_environment():
    """设置环境变量（用于测试）"""
    if not os.getenv('TELEGRAM_BOT_TOKEN'):
        print("⚠️ Setting default environment variables for testing...")
        os.environ['TELEGRAM_BOT_TOKEN'] = 'test-token'
        os.environ['TELEGRAM_BOT_USERNAME'] = 'test_bot'
        os.environ['AWS_REGION'] = 'us-east-1'
        os.environ['DYNAMODB_TABLE_PREFIX'] = 'test-table'


def initialize_tables():
    """初始化所有表格"""
    print("🚀 Step 1: Initializing DynamoDB tables...")
    
    initializer = DynamoDBInitializer()
    
    # 显示当前表格
    print("\n📋 Current tables:")
    initializer.list_tables()
    
    # 创建表格
    success = initializer.initialize_all_tables()
    
    if success:
        print("\n✅ All tables initialized successfully!")
        
        # 再次显示表格
        print("\n📋 Tables after initialization:")
        initializer.list_tables()
        
        return True
    else:
        print("\n❌ Failed to initialize all tables")
        return False


def test_database_operations():
    """测试数据库操作"""
    print("\n🧪 Step 2: Testing database operations...")
    
    db = DatabaseManager()
    
    # 测试用户操作
    print("\n👤 Testing user operations...")
    
    # 创建用户
    user_id = "123456789"
    username = "testuser"
    db.create_user(user_id, username, "zh")
    
    # 获取用户
    user = db.get_user(user_id)
    if user:
        print(f"✅ User retrieved: {user['username']}, status: {user['status']}")
    else:
        print("❌ Failed to retrieve user")
    
    # 更新用户状态
    db.update_user_status(user_id, "premium-user")
    
    # 测试群组操作
    print("\n👥 Testing group operations...")
    
    # 创建群组
    group_id = "-1001234567890"
    db.create_group(group_id, "supergroup", "Test Group")
    
    # 获取群组
    group = db.get_group(group_id)
    if group:
        print(f"✅ Group retrieved: {group.get('title', 'No title')}, status: {group['status']}")
    else:
        print("❌ Failed to retrieve group")
    
    # 测试转录任务操作
    print("\n🎵 Testing transcription job operations...")
    
    # 创建转录任务
    audio_files = [
        {
            "file_id": "BAADBAADrwADBREAAYag2XT...",
            "file_name": "test_song.mp3",
            "file_size": 5242880,
            "duration": 180,
            "mime_type": "audio/mpeg"
        }
    ]
    
    db.create_transcription_job(user_id, group_id, audio_files)
    
    # 获取转录任务
    job = db.get_transcription_job(user_id, group_id)
    if job:
        print(f"✅ Job retrieved: status={job['job_status']}, files={len(job['audio_files'])}")
    else:
        print("❌ Failed to retrieve transcription job")
    
    # 添加更多音频文件
    new_audio_file = {
        "file_id": "BAADBAADsAADBREAAYag2XT...",
        "file_name": "another_song.mp3",
        "file_size": 3000000,
        "duration": 120,
        "mime_type": "audio/mpeg"
    }
    
    db.add_audio_file(user_id, group_id, new_audio_file)
    
    # 更新任务状态
    db.update_job_status(user_id, group_id, "ready_to_start")
    
    # 开始处理
    db.update_job_status(user_id, group_id, "processing", job_id="job_abc123", message_id=456)
    
    # 完成任务
    results = [
        {
            "this_message_id": 789,
            "reply_to_message_id": 456,
            "source_file_id": "BAADBAADrwADBREAAYag2XT...",
            "transcription": "测试歌词内容...",
            "format": "lrc",
            "language": "zh"
        }
    ]
    
    statistics = {
        "gpu_seconds": 120,
        "gpu_backend": "AWS",
        "audio_seconds": 300,
        "speed_factor": 2.5,
        "processing_time": 180
    }
    
    db.complete_job(user_id, group_id, results, statistics)
    
    # 获取最终结果
    final_job = db.get_transcription_job(user_id, group_id)
    if final_job:
        print(f"✅ Final job status: {final_job['job_status']}")
        print(f"✅ Results count: {len(final_job.get('results', []))}")
        print(f"✅ Statistics: {final_job.get('statistics', {})}")
    
    print("\n🎉 All database operations completed successfully!")


def main():
    """主函数"""
    print("🔧 DynamoDB Setup Script")
    print("=" * 50)

    parser = argparse.ArgumentParser(description="DynamoDB Setup Script")
    parser.add_argument('--init-only', action='store_true', help='Only initialize tables, do not run tests.')
    args = parser.parse_args()
    
    # 设置环境变量
    setup_environment()
    
    # 验证配置
    if not config.validate_config():
        print("❌ Configuration validation failed")
        sys.exit(1)
    
    try:
        # 初始化表格
        if not initialize_tables():
            print("❌ Failed to initialize tables")
            sys.exit(1)
        
        # 如果不是仅初始化，则测试数据库操作
        if not args.init_only:
            test_database_operations()
        
        print("\n✅ Setup completed successfully!")
        
        if not args.init_only:
            print("\n📚 Next steps:")
            print("1. Update your Lambda function to use the database classes")
            print("2. Set proper AWS credentials and region")
            print("3. Test with real Telegram bot interactions")
        
    except Exception as e:
        print(f"❌ Setup failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 