from typing import Dict, Any
from message_classifier import MessageClassification
from telegram_client import TelegramClient, MockTelegramClient
from config import config


class MessageHandler:
    """消息处理器"""
    
    def __init__(self, telegram_bot_token: str = None, use_mock_client: bool = False):
        self.bot_token = telegram_bot_token or config.bot_token
        
        # 根据参数选择使用真实客户端还是Mock客户端
        if use_mock_client:
            self.telegram = MockTelegramClient(self.bot_token)
        else:
            self.telegram = TelegramClient(self.bot_token)
        
        # 这里将来可以初始化DynamoDB, S3等服务
    
    def handle_message(self, message: Dict[str, Any], classification: MessageClassification):
        """
        根据分类结果处理消息
        
        Args:
            message: Telegram消息对象
            classification: 消息分类结果
        """
        chat_id = message['chat']['id']
        
        print(f"\n🔄 Processing {classification.message_type} message in {classification.chat_type} chat")
        
        # 发送正在输入状态
        self.telegram.send_typing_action(chat_id)
        
        if classification.chat_type == 'private':
            self._handle_private_chat(message, classification)
        elif classification.chat_type == 'group':
            self._handle_group_chat(message, classification)
        else:
            print(f"⚠️ Unknown chat type: {classification.chat_type}")
            self.telegram.send_message(
                chat_id, 
                "❌ Sorry, I can only work in [private chats] and [groups]."
            )
    
    def _handle_private_chat(self, message: Dict[str, Any], classification: MessageClassification):
        """处理私聊消息"""
        if classification.message_type == 'command':
            self._handle_private_command(message, classification)
        elif classification.message_type == 'media' and classification.contains_audio:
            self._handle_private_audio(message, classification)
        elif classification.message_type == 'text':
            self._handle_private_text(message, classification)
        else:
            print(f"📝 Private chat: Ignoring {classification.message_type} message")
            # 对于不支持的消息类型，不发送回应以避免干扰用户
    
    def _handle_group_chat(self, message: Dict[str, Any], classification: MessageClassification):
        """处理群聊消息"""
        if classification.message_type == 'command':
            self._handle_group_command(message, classification)
        elif classification.message_type == 'media' and classification.contains_audio:
            self._handle_group_audio(message, classification)
        else:
            print(f"📝 Group chat: Ignoring {classification.message_type} message")
            # 群聊中不对普通消息做回应
    
    def _handle_private_command(self, message: Dict[str, Any], classification: MessageClassification):
        """处理命令（私聊）"""
        command = classification.command.lower()
        chat_id = message['chat']['id']
        
        print(f"🤖 Processing command: {command}")
        
        if command == '/start':
            self._handle_start_command(message)
        elif command == '/help':
            self._handle_help_command(message)
        elif command == '/mylist':
            self._handle_mylist_command(message)
        elif command == '/setlang':
            self._handle_setlang_command(message)
        elif command.startswith('/remove'):
            self._handle_remove_command(message)
        else:
            print(f"❓ Unknown command: {command}")
            self.telegram.send_message(
                chat_id,
                f"❓ Unknown command: {command}\n\n"
                "Use /help to see available commands."
            )
    
    def _handle_group_command(self, message: Dict[str, Any], classification: MessageClassification):
        """处理群聊命令"""
        command = classification.command.lower()
        chat_id = message['chat']['id']
        
        print(f"🤖 Processing group command: {command}")
        
        # 使用配置文件中的方法检查命令是否针对当前bot
        if config.is_command_for_this_bot(command):
            base_command = command.split('@')[0]
            
            if base_command == '/start':
                self._handle_start_command(message)
            elif base_command == '/add_music':
                self._handle_add_music_command(message)
            elif base_command == '/remove':
                self._handle_remove_command(message)
            elif base_command == '/mylist':
                self._handle_mylist_command(message)
            else:
                print(f"❓ Unknown group command: {base_command}")
                self.telegram.send_message(
                    chat_id,
                    f"❓ Unknown command: {base_command}\n\n"
                    "Use /help to see available commands."
                )
        else:
            print(f"📝 Group command not addressed to bot: {command}")
            # 不是给当前bot的命令，不做回应
    
    def _handle_private_audio(self, message: Dict[str, Any], classification: MessageClassification):
        """处理私聊音频文件"""
        chat_id = message['chat']['id']
        user_name = message.get('from', {}).get('first_name', 'User')
        
        print(f"🎵 Processing audio in private chat")
        print(f"   - Audio files count: {len(classification.audio_files)}")
        print(f"   - Is grouped media: {classification.is_grouped_media}")
        
        if classification.is_grouped_media:
            print(f"   - Media group ID: {classification.media_group_id}")
            print("   - Action: Add all files in media group to transcription list")
            
            self.telegram.send_message(
                chat_id,
                f"🎵 Audio album detected! I've added {len(classification.audio_files)} files to your transcription queue.\n\n"
                "I'll process them in order and send you the transcripts when ready.\n\n"
                "Use /mylist to check your queue status."
            )
        else:
            print("   - Action: Add single audio file to transcription list")
            
            audio = classification.audio_files[0]
            file_name = audio.get('file_name', 'audio file')
            duration = audio.get('duration')
            duration_text = f" ({duration}s)" if duration else ""
            
            self.telegram.send_message(
                chat_id,
                f"🎵 Audio file received: <b>{file_name}</b>{duration_text}\n\n"
                "I've added it to your transcription queue. I'll send you the transcript when it's ready!\n\n"
                "Use /mylist to check your queue status.",
                parse_mode='HTML'
            )
        
        # 这里将来实现添加到DynamoDB转录列表的逻辑
        for i, audio in enumerate(classification.audio_files):
            print(f"   - Audio {i+1}: {audio.get('file_name', 'N/A')} ({audio.get('file_size', 0)} bytes)")
    
    def _handle_group_audio(self, message: Dict[str, Any], classification: MessageClassification):
        """处理群聊音频文件"""
        print(f"🎵 Processing audio in group chat")
        print(f"   - Audio files count: {len(classification.audio_files)}")
        print(f"   - Action: Audio detected but waiting for /add_music@bot command")
        
        # 在群聊中，音频文件不会立即添加，需要等待用户使用 /add_music@bot 命令
        # 这里不发送消息，避免在群聊中产生过多噪音
        
        for i, audio in enumerate(classification.audio_files):
            print(f"   - Audio {i+1}: {audio.get('file_name', 'N/A')} ({audio.get('file_size', 0)} bytes)")
    
    def _handle_private_text(self, message: Dict[str, Any], classification: MessageClassification):
        """处理私聊文本消息"""
        text = message.get('text', '')
        chat_id = message['chat']['id']
        
        print(f"💬 Processing text message in private chat: '{text[:50]}...'")
        
        # 检查是否是回复消息
        if 'reply_to_message' in message:
            self._handle_reply_message(message, classification)
        else:
            print("   - Action: Regular text message, no special handling needed")
            
            # 对于常规文本消息，提供友好的回应
            self.telegram.send_message(
                chat_id,
                "👋 Hi! I'm a voice transcription bot.\n\n"
                "Send me audio files and I'll transcribe them for you!\n\n"
                "Use /help to see what I can do."
            )
    
    def _handle_reply_message(self, message: Dict[str, Any], classification: MessageClassification):
        """处理回复消息"""
        reply_to = message['reply_to_message']
        chat_id = message['chat']['id']
        text = message.get('text', '').lower()
        
        print(f"↩️ Processing reply message")
        
        # 检查回复的消息是否包含音频
        if 'audio' in reply_to or 'document' in reply_to:
            print("   - Reply to audio message detected")
            print("   - Action: Add replied audio to transcription list")
            
            # 检查用户是否想要添加音频到转录列表
            if any(keyword in text for keyword in ['add', 'transcribe', 'convert', '转录', '添加']):
                audio_name = "this audio"
                if 'audio' in reply_to:
                    audio_name = reply_to['audio'].get('file_name', 'this audio')
                elif 'document' in reply_to:
                    audio_name = reply_to['document'].get('file_name', 'this audio')
                
                self.telegram.send_message(
                    chat_id,
                    f"✅ Got it! I've added <b>{audio_name}</b> to your transcription queue.\n\n"
                    "I'll send you the transcript when it's ready!\n\n"
                    "Use /mylist to check your queue status.",
                    parse_mode='HTML',
                    reply_to_message_id=message['message_id']
                )
            else:
                # 如果不是明确的添加请求，提供提示
                self.telegram.send_message(
                    chat_id,
                    "🎵 I see you're replying to an audio message!\n\n"
                    "If you want me to transcribe it, just say 'add this' or 'transcribe this'.",
                    reply_to_message_id=message['message_id']
                )
            
            # 检查是否为媒体组
            if 'media_group_id' in reply_to:
                print(f"   - Replied message is part of media group: {reply_to['media_group_id']}")
                print("   - Action: Add entire media group to transcription list")
        else:
            print("   - Reply to non-audio message, no special handling")
            # 对于回复非音频消息，不做特殊处理
    
    def _handle_start_command(self, message: Dict[str, Any]):
        """处理 /start 命令"""
        user_name = message.get('from', {}).get('first_name', 'User')
        chat_id = message['chat']['id']
        
        print(f"🚀 Start command from user: {user_name}")
        print("   - Action: Send welcome message")
        
        welcome_text = f"👋 Hello <b>{user_name}</b>! Welcome to the Voice Transcription Bot!\n\n" \
                      "🎵 <b>What I can do:</b>\n" \
                      "• Transcribe audio files to text\n" \
                      "• Support multiple languages\n" \
                      "• Handle audio albums (media groups)\n" \
                      "• Work in both private chats and groups\n\n" \
                      "📤 <b>How to use:</b>\n" \
                      "• In private chat: Just send me audio files!\n" \
                      f"• In groups: Use /add_music{config.get_bot_mention()} command\n\n" \
                      "Type /help for more commands!"
        
        self.telegram.send_message(chat_id, welcome_text, parse_mode='HTML')
    
    def _handle_help_command(self, message: Dict[str, Any]):
        """处理 /help 命令"""
        chat_id = message['chat']['id']
        
        print("❓ Help command")
        print("   - Action: Send help message")
        
        help_text = "🆘 <b>Available Commands:</b>\n\n" \
                   "🏠 <b>Private Chat:</b>\n" \
                   "• /start - Show welcome message\n" \
                   "• /help - Show this help\n" \
                   "• /mylist - Show your transcription queue\n" \
                   "• /setlang - Change transcription language\n" \
                   "• /remove \<item_id\> - Remove item from queue\n\n" \
                   "👥 <b>Group Chat:</b>\n" \
                   f"• /start{config.get_bot_mention()} - Show welcome message\n" \
                   f"• /add_music{config.get_bot_mention()} - Add replied audio to queue\n" \
                   f"• /mylist{config.get_bot_mention()} - Show your queue\n" \
                   f"• /remove{config.get_bot_mention()} \<item_id\> - Remove item\n\n" \
                   "🎵 <b>Supported formats:</b>\n" \
                   "MP3, MP4, M4A, WAV, FLAC, OGG, WebM"
        
        self.telegram.send_message(chat_id, help_text, parse_mode='HTML')
    
    def _handle_mylist_command(self, message: Dict[str, Any]):
        """处理 /mylist 命令"""
        chat_id = message['chat']['id']
        user_id = message.get('from', {}).get('id')
        
        print("📋 MyList command")
        print("   - Action: Show user's transcription to-do list")
        
        # 这里将来从DynamoDB获取用户的转录队列
        # 现在先显示示例响应
        self.telegram.send_message(
            chat_id,
            "📋 <b>Your Transcription Queue:</b>\n\n"
            "🔄 <b>Processing:</b>\n"
            "• sample_song.mp3 (3:45) - 50% complete\n\n"
            "⏳ <b>Waiting:</b>\n"
            "• album_track_1.mp3 (4:12)\n"
            "• album_track_2.mp3 (3:58)\n\n"
            "✅ <b>Completed today:</b>\n"
            "• previous_audio.mp3 - Download transcript\n\n"
            "Use /remove \<item_id\> to cancel items.",
            parse_mode='HTML'
        )
    
    def _handle_setlang_command(self, message: Dict[str, Any]):
        """处理 /setlang 命令"""
        chat_id = message['chat']['id']
        
        print("🌐 SetLang command")
        print("   - Action: Show language selection menu")
        
        # 创建语言选择键盘
        keyboard = []
        languages = {
            'en': '🇺🇸 English',
            'zh': '🇨🇳 Chinese',
            'ja': '🇯🇵 Japanese',
            'ko': '🇰🇷 Korean',
            'es': '🇪🇸 Spanish',
            'fr': '🇫🇷 French',
            'de': '🇩🇪 German',
            'ru': '🇷🇺 Russian'
        }
        
        # 每行2个按钮
        row = []
        for lang_code, lang_name in languages.items():
            row.append({'text': lang_name, 'callback_data': f'setlang_{lang_code}'})
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:  # 添加剩余的按钮
            keyboard.append(row)
        
        self.telegram.send_inline_keyboard(
            chat_id,
            "🌐 <b>Select Transcription Language:</b>\n\n"
            "Choose the language for audio transcription:",
            keyboard,
            reply_to_message_id=message['message_id']
        )
    
    def _handle_remove_command(self, message: Dict[str, Any]):
        """处理 /remove 命令"""
        text = message.get('text', '')
        chat_id = message['chat']['id']
        
        print(f"🗑️ Remove command: {text}")
        print("   - Action: Remove item from transcription list")
        
        # 解析命令参数
        parts = text.split()
        if len(parts) < 2:
            self.telegram.send_message(
                chat_id,
                "❌ Please specify an item ID to remove.\n\n"
                "Usage: /remove \<item_id\>\n"
                "Use /mylist to see your queue with item IDs.",
                reply_to_message_id=message['message_id']
            )
            return
        
        item_id = parts[1]
        
        # 这里将来实现从DynamoDB删除项目的逻辑
        self.telegram.send_message(
            chat_id,
            f"✅ Removed item <b>{item_id}</b> from your transcription queue.\n\n"
            "Use /mylist to see your updated queue.",
            parse_mode='HTML',
            reply_to_message_id=message['message_id']
        )
    
    def _handle_add_music_command(self, message: Dict[str, Any]):
        """处理 /add_music 命令（群聊）"""
        chat_id = message['chat']['id']
        user_name = message.get('from', {}).get('first_name', 'User')
        
        print("➕ Add music command in group")
        
        if 'reply_to_message' in message:
            reply_to = message['reply_to_message']
            if 'audio' in reply_to or 'document' in reply_to:
                print("   - Replying to audio message")
                print("   - Action: Add replied audio to user's transcription list")
                
                audio_name = "audio file"
                if 'audio' in reply_to:
                    audio_name = reply_to['audio'].get('file_name', 'audio file')
                elif 'document' in reply_to:
                    audio_name = reply_to['document'].get('file_name', 'audio file')
                
                self.telegram.send_message(
                    chat_id,
                    f"✅ <b>{user_name}</b>, I've added <b>{audio_name}</b> to your personal transcription queue!\n\n"
                    "I'll send you the transcript in our private chat when it's ready.",
                    parse_mode='HTML',
                    reply_to_message_id=message['message_id']
                )
            else:
                print("   - Not replying to audio message")
                self.telegram.send_message(
                    chat_id,
                    f"❌ <b>{user_name}</b>, please reply to an audio message when using this command.",
                    parse_mode='HTML',
                    reply_to_message_id=message['message_id']
                )
        else:
            print("   - Not a reply to any message")
            self.telegram.send_message(
                chat_id,
                f"❌ <b>{user_name}</b>, please reply to an audio message when using {config.get_bot_mention()}.",
                parse_mode='HTML',
                reply_to_message_id=message['message_id']
            ) 