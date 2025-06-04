import json
from typing import Dict, Any
from message_classifier import MessageClassifier
from message_handler import MessageHandler
from config import config


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda处理函数
    
    Args:
        event: Lambda事件，包含Telegram webhook数据
        context: Lambda上下文
        
    Returns:
        HTTP响应
    """
    try:
        # 验证配置
        if not config.validate_config():
            print("❌ Bot configuration is invalid")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Bot configuration is invalid'})
            }
        
        print(f"📨 Received event: {json.dumps(event)}")
        
        # 解析webhook数据
        if isinstance(event.get('body'), str):
            webhook_data = json.loads(event['body'])
        else:
            webhook_data = event.get('body') or event
        
        # 提取消息
        if not webhook_data or 'message' not in webhook_data:
            print("⚠️ No message in webhook data")
            return {
                'statusCode': 200,
                'body': json.dumps({'status': 'no_message'})
            }
        
        message = webhook_data['message']
        
        # 初始化分类器和处理器
        classifier = MessageClassifier()
        handler = MessageHandler()  # 使用真实的Telegram客户端
        
        # 分类消息
        classification = classifier.classify_message(message)
        
        # 处理消息
        handler.handle_message(message, classification)
        
        print("✅ Message processed successfully")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'success',
                'chat_type': classification.chat_type,
                'message_type': classification.message_type,
                'contains_audio': classification.contains_audio
            })
        }
        
    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        # 重要：即使出错也返回200，防止Telegram重复发送更新
        return {
            'statusCode': 200,
            'body': json.dumps({'error': str(e)})
        }


def handle_test_message(test_message: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理测试消息（用于本地测试）
    
    Args:
        test_message: 测试消息数据
        
    Returns:
        处理结果
    """
    try:
        print("🧪 Processing test message...")
        
        # 使用Mock客户端进行测试
        classifier = MessageClassifier()
        handler = MessageHandler(use_mock_client=True)
        
        # 分类和处理消息
        classification = classifier.classify_message(test_message)
        handler.handle_message(test_message, classification)
        
        return {
            'status': 'success',
            'classification': {
                'chat_type': classification.chat_type,
                'message_type': classification.message_type,
                'contains_audio': classification.contains_audio,
                'is_grouped_media': classification.is_grouped_media,
                'audio_files_count': len(classification.audio_files)
            }
        }
        
    except Exception as e:
        print(f"❌ Error processing test message: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }


# 本地测试用例
if __name__ == "__main__":
    # 测试/start命令
    test_start_command = {
        "message": {
            "message_id": 1001,
            "from": {
                "id": 111111111,
                "is_bot": False,
                "first_name": "TestUser",
                "username": "testuser"
            },
            "chat": {
                "id": 111111111,
                "type": "private"
            },
            "date": 1589912678,
            "text": "/start"
        }
    }
    
    print("🧪 Testing /start command...")
    result = handle_test_message(test_start_command['message'])
    print(f"Result: {result}")
    
    # 测试音频文件
    test_audio_message = {
        "message": {
            "message_id": 1002,
            "from": {
                "id": 111111111,
                "is_bot": False,
                "first_name": "TestUser",
                "username": "testuser"
            },
            "chat": {
                "id": 111111111,
                "type": "private"
            },
            "date": 1589912679,
            "audio": {
                "duration": 180,
                "file_name": "test_audio.mp3",
                "mime_type": "audio/mpeg",
                "file_id": "AUDIO_FILE_ID_TEST",
                "file_unique_id": "AUDIO_UNIQUE_TEST",
                "file_size": 5000000
            }
        }
    }
    
    print("\n🧪 Testing audio message...")
    result = handle_test_message(test_audio_message['message'])
    print(f"Result: {result}") 