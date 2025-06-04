# Telegram Bot Message Classification Testing

本文档说明如何使用测试模块来验证 Telegram 消息分类和处理功能。

## 测试模块概述

- **`test_message_classification.py`** - 主测试模块，包含各种 Telegram 消息测试用例
- **`message_classifier.py`** - 消息分类器
- **`message_handler.py`** - 消息处理器
- **`lambda_function.py`** - 简化的主入口文件

## 测试用例覆盖

### 私聊测试用例 (Private Chat)
1. **`private_start_command`** - 私聊 /start 命令
2. **`private_forwarded_audio`** - 私聊转发音频文件（来自频道，document类型）
3. **`private_single_audio_with_caption`** - 私聊上传单个音频文件（带标题）
4. **`private_media_group_part1`** - 私聊媒体组 - 第1个音频文件
5. **`private_reply_to_media_group`** - 私聊回复媒体组消息
6. **`private_text_message`** - 私聊普通文本消息

### 群聊测试用例 (Group Chat)

#### Non-Privacy Mode
1. **`group_start_command_with_bot_mention`** - 群聊 @bot 的 /start 命令
2. **`group_start_command_without_mention`** - 群聊不带 @bot 的 /start 命令
3. **`group_single_audio`** - 群聊上传单个音频文件
4. **`group_media_group_part1`** - 群聊媒体组 - 第1个音频文件
5. **`group_add_music_reply`** - 群聊回复音频消息使用 /add_music@bot 命令
6. **`group_other_user_add_music`** - 群聊其他用户回复音频消息使用 /add_music@bot 命令
7. **`group_forwarded_audio_from_channel`** - 群聊转发音频（来自频道，document类型）

#### Privacy Mode
1. **`group_privacy_bot_command_with_mention`** - 群聊隐私模式：@bot 命令
2. **`group_privacy_reply_to_bot`** - 群聊隐私模式：回复bot消息

### 其他测试用例
1. **`unknown_command`** - 未知命令

## 运行测试

### 1. 运行所有测试
```bash
cd bot-src
python test_message_classification.py
```
或
```bash
python test_message_classification.py all
```

### 2. 运行特定类别的测试

#### 只运行私聊测试
```bash
python test_message_classification.py private
```

#### 只运行群聊测试
```bash
python test_message_classification.py group
```

### 3. 运行单个测试用例
```bash
python test_message_classification.py private_start_command
python test_message_classification.py group_add_music_reply
python test_message_classification.py private_media_group_part1
```

## 测试输出示例

### 分类结果输出
```
==================================================
MESSAGE CLASSIFICATION RESULT
==================================================
Chat Type: private
Message Type: media
Contains Audio: true
Is Grouped Media: true
Media Group ID: 13980518987791237
Audio Files Count: 1
  Audio 1:
    File Name: album_track_1.mp3
    File Size: 9152189 bytes
    Duration: 225 seconds
    MIME Type: audio/mpeg
    Media Type: audio
Chat ID: 111111111
User ID: 111111111
Message ID: 1004
==================================================
```

### 处理结果输出
```
🔄 Processing media message in private chat
🎵 Processing audio in private chat
   - Audio files count: 1
   - Is grouped media: true
   - Media group ID: 13980518987791237
   - Action: Add all files in media group to transcription list
   - Audio 1: album_track_1.mp3 (9152189 bytes)
```

### 测试总结输出
```
======================================================================
📊 TEST SUMMARY
======================================================================
✅ Passed: 15
❌ Failed: 0
📈 Success Rate: 100.0%
======================================================================
```

## 测试数据说明

所有测试用例都使用匿名化的测试数据，包括：
- 用户信息：使用通用的测试用户名和ID
- 文件名：使用通用的文件命名（如 `sample_song.mp3`、`album_track_1.mp3`）
- 频道和群组：使用通用的测试名称（如 `Test Group`、`Music Channel`）
- 所有敏感信息都已被替换为测试友好的匿名数据

测试覆盖了以下关键场景：
- ✅ Private Chat vs Group Chat 分类
- ✅ Text vs Media vs Command 分类
- ✅ Audio 检测（audio 和 document 类型）
- ✅ Media Group 检测
- ✅ 转发消息处理
- ✅ 回复消息处理
- ✅ 群聊 Privacy Mode 和 Non-Privacy Mode
- ✅ 各种命令处理

## 扩展测试

如需添加新的测试用例，请在 `TelegramMessageTester._load_test_cases()` 方法中添加新的测试数据。测试用例格式：

```python
"test_case_name": {
    "description": "测试用例描述",
    "update_id": 123456789,
    "message": {
        # Telegram 消息对象
    }
}
```

## 注意事项

1. 测试模块使用模拟的 bot token (`test_bot_token`)，不会发送真实消息
2. 所有测试用例都使用匿名化的测试数据，适合公开仓库
3. 测试覆盖了音频文件的两种形式：`audio` 字段和 `document` 字段
4. 媒体组消息需要多个测试用例来模拟完整的媒体组
5. 测试数据基于真实的 Telegram 消息格式，但所有个人信息都已匿名化 