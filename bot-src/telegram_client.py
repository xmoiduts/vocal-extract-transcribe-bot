import requests
import json
from typing import Dict, Any, Optional, List
from config import config


class TelegramClient:
    """Telegram API客户端"""
    
    def __init__(self, bot_token: str = None):
        self.bot_token = bot_token or config.bot_token
        self.api_base = f"{config.telegram_api_base}/bot{self.bot_token}"
    
    def send_message(self, chat_id: int, text: str, 
                     parse_mode: str = 'HTML',
                     reply_to_message_id: Optional[int] = None,
                     disable_notification: bool = False) -> Dict[str, Any]:
        """
        发送文本消息
        
        Args:
            chat_id: 聊天ID
            text: 消息文本
            parse_mode: 解析模式 ('HTML', 'Markdown', None)
            reply_to_message_id: 回复的消息ID
            disable_notification: 是否静默发送
            
        Returns:
            Telegram API响应
        """
        url = f"{self.api_base}/sendMessage"
        
        payload = {
            'chat_id': chat_id,
            'text': text,
            'disable_notification': disable_notification
        }
        
        if parse_mode:
            payload['parse_mode'] = parse_mode
            
        if reply_to_message_id:
            payload['reply_to_message_id'] = reply_to_message_id
        
        try:
            response = requests.post(url, data=payload, timeout=30)
            print(f"📱 TELEGRAM RESPONSE to chat {chat_id}:")
            print(f"   response.json()")
            return response.json()
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return {"ok": False, "error": str(e)}
    
    def send_typing_action(self, chat_id: int) -> Dict[str, Any]:
        """
        发送正在输入状态
        
        Args:
            chat_id: 聊天ID
            
        Returns:
            Telegram API响应
        """
        url = f"{self.api_base}/sendChatAction"
        
        payload = {
            'chat_id': chat_id,
            'action': 'typing'
        }
        
        try:
            response = requests.post(url, data=payload, timeout=10)
            return response.json()
        except Exception as e:
            print(f"❌ Error sending typing action: {e}")
            return {"ok": False, "error": str(e)}
    
    def get_file(self, file_id: str) -> Dict[str, Any]:
        """
        获取文件信息
        
        Args:
            file_id: 文件ID
            
        Returns:
            文件信息
        """
        url = f"{self.api_base}/getFile"
        
        payload = {
            'file_id': file_id
        }
        
        try:
            response = requests.post(url, data=payload, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ Error getting file info: {e}")
            return {"ok": False, "error": str(e)}
        
    # TODO: get file list by media group id? Should it be put here or in the handler logic?
    
    def download_file(self, file_path: str) -> Optional[bytes]:
        """
        下载文件
        
        Args:
            file_path: 文件路径（从getFile获取）
            
        Returns:
            文件内容字节数组
        """
        url = f"https://api.telegram.org/file/bot{self.bot_token}/{file_path}"
        
        try:
            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                return response.content
            else:
                print(f"❌ Error downloading file: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error downloading file: {e}")
            return None
    
    def send_inline_keyboard(self, chat_id: int, text: str, 
                           keyboard: List[List[Dict[str, str]]],
                           reply_to_message_id: Optional[int] = None) -> Dict[str, Any]:
        """
        发送带内联键盘的消息
        
        Args:
            chat_id: 聊天ID
            text: 消息文本
            keyboard: 内联键盘按钮数组
            reply_to_message_id: 回复的消息ID
            
        Returns:
            Telegram API响应
        """
        url = f"{self.api_base}/sendMessage"
        
        payload = {
            'chat_id': chat_id,
            'text': text,
            'reply_markup': json.dumps({
                'inline_keyboard': keyboard
            })
        }
        
        if reply_to_message_id:
            payload['reply_to_message_id'] = reply_to_message_id
        
        try:
            response = requests.post(url, data=payload, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ Error sending keyboard message: {e}")
            return {"ok": False, "error": str(e)}


class MockTelegramClient(TelegramClient):
    """Mock Telegram客户端用于测试"""
    
    def __init__(self, bot_token: str = "test_token"):
        self.bot_token = bot_token
        self.sent_messages = []  # 存储发送的消息用于测试验证
    
    def send_message(self, chat_id: int, text: str, 
                     parse_mode: str = 'HTML',
                     reply_to_message_id: Optional[int] = None,
                     disable_notification: bool = False) -> Dict[str, Any]:
        """Mock发送消息"""
        message = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'reply_to_message_id': reply_to_message_id,
            'disable_notification': disable_notification
        }
        
        self.sent_messages.append(message)
        
        # 输出到控制台以便测试时查看
        print(f"📱 TELEGRAM RESPONSE to chat {chat_id}:")
        print(f"   {text}")
        
        return {"ok": True, "message_id": len(self.sent_messages)}
    
    def send_typing_action(self, chat_id: int) -> Dict[str, Any]:
        """Mock发送输入状态"""
        print(f"⌨️ Typing action sent to chat {chat_id}")
        return {"ok": True}
    
    def send_inline_keyboard(self, chat_id: int, text: str, 
                           keyboard: List[List[Dict[str, str]]],
                           reply_to_message_id: Optional[int] = None) -> Dict[str, Any]:
        """Mock发送键盘消息"""
        message = {
            'chat_id': chat_id,
            'text': text,
            'keyboard': keyboard,
            'reply_to_message_id': reply_to_message_id
        }
        
        self.sent_messages.append(message)
        
        print(f"📱 TELEGRAM KEYBOARD RESPONSE to chat {chat_id}:")
        print(f"   {text}")
        print(f"   Keyboard: {keyboard}")
        
        return {"ok": True, "message_id": len(self.sent_messages)} 