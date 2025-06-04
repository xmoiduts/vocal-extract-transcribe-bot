from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class MessageClassification:
    """消息分类结果"""
    chat_type: str  # 'private' or 'group'
    message_type: str  # 'text', 'media', 'command'
    contains_audio: bool
    is_grouped_media: bool
    media_group_id: Optional[str] = None
    audio_files: List[Dict[str, Any]] = None
    command: Optional[str] = None
    
    def __post_init__(self):
        if self.audio_files is None:
            self.audio_files = []


class MessageClassifier:
    """Telegram消息分类器"""
    
    def __init__(self):
        # 支持的音频MIME类型
        self.audio_mime_types = {
            'audio/mpeg', 'audio/mp3', 'audio/mp4', 'audio/aac', 
            'audio/ogg', 'audio/wav', 'audio/flac', 'audio/m4a',
            'audio/x-m4a', 'audio/webm'
        }
        # 支持的包含音频轨道的视频MIME类型
        self.video_with_audio_mime_types = {
            'video/mp4', 'video/avi', 'video/mkv', 'video/mov',
            'video/webm', 'video/ogg', 'video/quicktime', 'video/x-msvideo'
        }
    
    def classify_message(self, message: Dict[str, Any]) -> MessageClassification:
        """
        对Telegram消息进行分类
        
        Args:
            message: Telegram消息对象
            
        Returns:
            MessageClassification: 分类结果
        """
        # 1. 判断聊天类型
        chat_type = self._get_chat_type(message)
        
        # 2. 判断消息类型和内容
        message_type, command = self._get_message_type(message)
        
        # 3. 检查是否包含音频（包括主消息和回复消息）
        contains_audio, audio_files = self._check_audio_content(message)
        
        # 4. 检查是否为媒体组
        is_grouped_media, media_group_id = self._check_media_group(message)
        
        classification = MessageClassification(
            chat_type=chat_type,
            message_type=message_type,
            contains_audio=contains_audio,
            is_grouped_media=is_grouped_media,
            media_group_id=media_group_id,
            audio_files=audio_files,
            command=command
        )
        
        # 输出分类结果
        self._print_classification(message, classification)
        
        return classification
    
    def _get_chat_type(self, message: Dict[str, Any]) -> str:
        """判断聊天类型"""
        chat = message.get('chat', {})
        chat_type = chat.get('type', 'unknown')
        
        if chat_type == 'private':
            return 'private'
        elif chat_type in ['group', 'supergroup']:
            return 'group'
        else:
            return 'unknown'
    
    def _get_message_type(self, message: Dict[str, Any]) -> tuple[str, Optional[str]]:
        """判断消息类型"""
        # 检查是否有文本内容
        text = message.get('text', '').strip()
        
        # 检查是否为命令
        if text.startswith('/'):
            command = text.split()[0]  # 提取命令部分
            return 'command', command
        
        # 检查是否包含媒体（包括回复消息中的媒体）
        has_media = any(key in message for key in [
            'audio', 'document', 'photo', 'video', 'voice', 'video_note'
        ])
        
        # 检查回复消息中是否包含媒体
        if 'reply_to_message' in message:
            reply_has_media = any(key in message['reply_to_message'] for key in [
                'audio', 'document', 'photo', 'video', 'voice', 'video_note'
            ])
            has_media = has_media or reply_has_media
        
        if has_media:
            return 'media', None
        elif text:
            return 'text', None
        else:
            return 'unknown', None
    
    def _check_audio_content(self, message: Dict[str, Any]) -> tuple[bool, List[Dict[str, Any]]]:
        """检查消息是否包含音频内容（包括主消息和回复消息）"""
        audio_files = []
        
        # 检查主消息中的音频内容
        audio_files.extend(self._extract_audio_from_message(message))
        
        # 检查回复消息中的音频内容
        if 'reply_to_message' in message:
            reply_audio = self._extract_audio_from_message(message['reply_to_message'])
            audio_files.extend(reply_audio)
        
        return len(audio_files) > 0, audio_files
    
    def _extract_audio_from_message(self, msg: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从单个消息中提取音频文件"""
        audio_files = []
        
        # 检查audio字段
        if 'audio' in msg:
            audio_info = self._extract_audio_info(msg['audio'], 'audio')
            audio_files.append(audio_info)
        
        # 检查voice字段（语音消息）
        if 'voice' in msg:
            audio_info = self._extract_audio_info(msg['voice'], 'voice')
            audio_files.append(audio_info)
        
        # 检查video_note字段（视频消息）
        if 'video_note' in msg:
            audio_info = self._extract_audio_info(msg['video_note'], 'video_note')
            audio_files.append(audio_info)
        
        # 检查document字段中的音频文件
        if 'document' in msg:
            document = msg['document']
            mime_type = document.get('mime_type', '')
            if mime_type in self.audio_mime_types:
                audio_info = self._extract_audio_info(document, 'document')
                audio_files.append(audio_info)
        
        # 检查video字段中包含音频轨道的视频文件
        if 'video' in msg:
            video = msg['video']
            mime_type = video.get('mime_type', '')
            if mime_type in self.video_with_audio_mime_types:
                audio_info = self._extract_audio_info(video, 'video')
                audio_files.append(audio_info)
        
        return audio_files
    
    def _extract_audio_info(self, media_obj: Dict[str, Any], media_type: str) -> Dict[str, Any]:
        """提取音频文件信息"""
        return {
            'file_id': media_obj.get('file_id'),
            'file_unique_id': media_obj.get('file_unique_id'),
            'file_name': media_obj.get('file_name'),
            'file_size': media_obj.get('file_size'),
            'duration': media_obj.get('duration'),  # document类型可能没有duration
            'mime_type': media_obj.get('mime_type'),
            'title': media_obj.get('title'),
            'performer': media_obj.get('performer'),
            'media_type': media_type  # 'audio', 'document', 'video', 'voice', 'video_note'
        }
    
    def _check_media_group(self, message: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """检查是否为媒体组"""
        media_group_id = message.get('media_group_id')
        return media_group_id is not None, media_group_id
    
    def _print_classification(self, message: Dict[str, Any], classification: MessageClassification):
        """输出分类结果"""
        print("=" * 50)
        print("MESSAGE CLASSIFICATION RESULT")
        print("=" * 50)
        
        # 基本信息
        print(f"Chat Type: {classification.chat_type}")
        print(f"Message Type: {classification.message_type}")
        
        if classification.command:
            print(f"Command: {classification.command}")
        
        # 媒体信息
        print(f"Contains Audio: {classification.contains_audio}")
        print(f"Is Grouped Media: {classification.is_grouped_media}")
        
        if classification.media_group_id:
            print(f"Media Group ID: {classification.media_group_id}")
        
        # 音频文件详情
        if classification.audio_files:
            print(f"Audio Files Count: {len(classification.audio_files)}")
            for i, audio in enumerate(classification.audio_files):
                print(f"  Audio {i+1}:")
                print(f"    File Name: {audio.get('file_name', 'N/A')}")
                print(f"    File Size: {audio.get('file_size', 'N/A')} bytes")
                print(f"    Duration: {audio.get('duration', 'N/A')} seconds")
                print(f"    MIME Type: {audio.get('mime_type', 'N/A')}")
                print(f"    Media Type: {audio.get('media_type', 'N/A')}")
        
        # 原始消息信息
        chat_id = message.get('chat', {}).get('id')
        user_id = message.get('from', {}).get('id')
        message_id = message.get('message_id')
        
        print(f"Chat ID: {chat_id}")
        print(f"User ID: {user_id}")
        print(f"Message ID: {message_id}")
        
        print("=" * 50) 