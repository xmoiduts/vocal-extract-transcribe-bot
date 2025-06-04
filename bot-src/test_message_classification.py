import json
import sys
import os
from message_classifier import MessageClassifier
from message_handler import MessageHandler

# Add the current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TelegramMessageTester:
    """Telegram消息分类测试器"""
    
    def __init__(self):
        self.classifier = MessageClassifier()
        self.handler = MessageHandler("test_bot_token", use_mock_client=True)  # 使用Mock客户端
        self.test_cases = self._load_test_cases()
    
    def _load_test_cases(self):
        """加载测试用例"""
        return {
            # 私聊测试用例
            "private_start_command": {
                "description": "私聊 /start 命令",
                "update_id": 123456789,
                "message": {
                    "message_id": 1001,
                    "from": {
                        "id": 111111111,
                        "is_bot": False,
                        "first_name": "TestUser",
                        "last_name": "Demo",
                        "username": "testuser",
                        "language_code": "en"
                    },
                    "chat": {
                        "id": 111111111,
                        "first_name": "TestUser",
                        "last_name": "Demo", 
                        "username": "testuser",
                        "type": "private"
                    },
                    "date": 1589912678,
                    "text": "/start"
                }
            },
            
            "private_forwarded_audio": {
                "description": "私聊转发音频文件（来自频道，document类型）",
                "update_id": 123456880,
                "message": {
                    "message_id": 1002,
                    "from": {
                        "id": 111111111,
                        "is_bot": False,
                        "first_name": "TestUser",
                        "last_name": "Demo",
                        "username": "testuser",
                        "language_code": "en"
                    },
                    "chat": {
                        "id": 111111111,
                        "first_name": "TestUser",
                        "last_name": "Demo",
                        "username": "testuser",
                        "type": "private"
                    },
                    "date": 1747564215,
                    "forward_origin": {
                        "type": "channel",
                        "chat": {
                            "id": -1001000000001,
                            "title": "Music Channel",
                            "username": "music_channel_test",
                            "type": "channel"
                        },
                        "message_id": 91,
                        "date": 1746545001
                    },
                    "forward_from_chat": {
                        "id": -1001000000001,
                        "title": "Music Channel",
                        "username": "music_channel_test",
                        "type": "channel"
                    },
                    "forward_from_message_id": 91,
                    "forward_date": 1746545001,
                    "document": {
                        "file_name": "sample_song.mp3",
                        "mime_type": "audio/mpeg",
                        "file_id": "DOC_FILE_ID_001_SAMPLE_AUDIO_MP3",
                        "file_unique_id": "DOC_UNIQUE_001",
                        "file_size": 3287850
                    }
                }
            },
            
            "private_forwarded_video_with_audio": {
                "description": "私聊转发视频文件（包含音频轨道）",
                "update_id": 123456881,
                "message": {
                    "message_id": 1003,
                    "from": {
                        "id": 111111111,
                        "is_bot": False,
                        "first_name": "TestUser",
                        "last_name": "Demo",
                        "username": "testuser",
                        "language_code": "en"
                    },
                    "chat": {
                        "id": 111111111,
                        "first_name": "TestUser",
                        "last_name": "Demo",
                        "username": "testuser",
                        "type": "private"
                    },
                    "date": 1747564300,
                    "forward_origin": {
                        "type": "user",
                        "sender_user": {
                            "id": 222222222,
                            "is_bot": False,
                            "first_name": "OtherUser",
                            "username": "otheruser"
                        },
                        "date": 1747564250
                    },
                    "video": {
                        "duration": 180,
                        "width": 1920,
                        "height": 1080,
                        "file_name": "music_video.mp4",
                        "mime_type": "video/mp4",
                        "file_id": "VIDEO_FILE_ID_001_MUSIC_VIDEO_MP4",
                        "file_unique_id": "VIDEO_UNIQUE_001",
                        "file_size": 15340000
                    }
                }
            },
            
            "private_single_audio_with_caption": {
                "description": "私聊上传单个音频文件（带标题）",
                "update_id": 123456882,
                "message": {
                    "message_id": 1004,
                    "from": {
                        "id": 111111111,
                        "is_bot": False,
                        "first_name": "TestUser",
                        "last_name": "Demo",
                        "username": "testuser",
                        "language_code": "en"
                    },
                    "chat": {
                        "id": 111111111,
                        "first_name": "TestUser",
                        "last_name": "Demo",
                        "username": "testuser",
                        "type": "private"
                    },
                    "date": 1747564658,
                    "audio": {
                        "duration": 207,
                        "file_name": "music_track.mp3",
                        "mime_type": "audio/mpeg",
                        "file_id": "AUDIO_FILE_ID_001_MUSIC_TRACK_MP3",
                        "file_unique_id": "AUDIO_UNIQUE_001",
                        "file_size": 3438888
                    },
                    "caption": "test audio file"
                }
            },
            
            "private_media_group_part1": {
                "description": "私聊媒体组 - 第1个音频文件",
                "update_id": 123456883,
                "message": {
                    "message_id": 1005,
                    "from": {
                        "id": 111111111,
                        "is_bot": False,
                        "first_name": "TestUser",
                        "last_name": "Demo",
                        "username": "testuser",
                        "language_code": "en"
                    },
                    "chat": {
                        "id": 111111111,
                        "first_name": "TestUser",
                        "last_name": "Demo",
                        "username": "testuser",
                        "type": "private"
                    },
                    "date": 1747564873,
                    "media_group_id": "MEDIA_GROUP_TEST_001",
                    "audio": {
                        "duration": 225,
                        "file_name": "album_track_1.mp3",
                        "mime_type": "audio/mpeg",
                        "title": "Song Title 1",
                        "performer": "Test Artist",
                        "thumbnail": {
                            "file_id": "THUMBNAIL_FILE_ID_001",
                            "file_unique_id": "THUMB_UNIQUE_001",
                            "file_size": 29137,
                            "width": 320,
                            "height": 320
                        },
                        "thumb": {
                            "file_id": "THUMBNAIL_FILE_ID_001",
                            "file_unique_id": "THUMB_UNIQUE_001",
                            "file_size": 29137,
                            "width": 320,
                            "height": 320
                        },
                        "file_id": "AUDIO_FILE_ID_002_ALBUM_TRACK_1_MP3",
                        "file_unique_id": "AUDIO_UNIQUE_002",
                        "file_size": 9152189
                    }
                }
            },
            
            "private_reply_to_media_group": {
                "description": "私聊回复媒体组消息",
                "update_id": 123456884,
                "message": {
                    "message_id": 1006,
                    "from": {
                        "id": 111111111,
                        "is_bot": False,
                        "first_name": "TestUser",
                        "last_name": "Demo",
                        "username": "testuser",
                        "language_code": "en"
                    },
                    "chat": {
                        "id": 111111111,
                        "first_name": "TestUser",
                        "last_name": "Demo",
                        "username": "testuser",
                        "type": "private"
                    },
                    "date": 1747565220,
                    "reply_to_message": {
                        "message_id": 1005,
                        "from": {
                            "id": 111111111,
                            "is_bot": False,
                            "first_name": "TestUser",
                            "last_name": "Demo",
                            "username": "testuser",
                            "language_code": "en"
                        },
                        "chat": {
                            "id": 111111111,
                            "first_name": "TestUser",
                            "last_name": "Demo",
                            "username": "testuser",
                            "type": "private"
                        },
                        "date": 1747564873,
                        "media_group_id": "MEDIA_GROUP_TEST_001",
                        "audio": {
                            "duration": 231,
                            "file_name": "album_track_2.mp3",
                            "mime_type": "audio/mpeg",
                            "title": "Song Title 2",
                            "performer": "Test Artist",
                            "file_id": "AUDIO_FILE_ID_003_ALBUM_TRACK_2_MP3",
                            "file_unique_id": "AUDIO_UNIQUE_003",
                            "file_size": 9333657
                        }
                    },
                    "text": "add this to to-do list"
                }
            },

            # TODO: add 私聊转发文件场景
            
            # 群聊测试用例（Non-Privacy Mode）
            "group_start_command_with_bot_mention": {
                "description": "群聊 @bot 的 /start 命令",
                "update_id": 123456915,
                "message": {
                    "message_id": 2001,
                    "from": {
                        "id": 111111111,
                        "is_bot": False,
                        "first_name": "TestUser",
                        "last_name": "Demo",
                        "username": "testuser",
                        "language_code": "en"
                    },
                    "chat": {
                        "id": -1001000000002,
                        "title": "Test Group",
                        "type": "group",
                        "all_members_are_administrators": True
                    },
                    "date": 1748176725,
                    "text": "/start@vocal_transcribe_bot",
                    "entities": [
                        {
                            "offset": 0,
                            "length": 27,
                            "type": "bot_command"
                        }
                    ]
                }
            },
            
            "group_start_command_without_mention": {
                "description": "群聊不带 @bot 的 /start 命令",
                "update_id": 123456916,
                "message": {
                    "message_id": 2002,
                    "from": {
                        "id": 111111111,
                        "is_bot": False,
                        "first_name": "TestUser",
                        "last_name": "Demo",
                        "username": "testuser",
                        "language_code": "en"
                    },
                    "chat": {
                        "id": -1001000000002,
                        "title": "Test Group",
                        "type": "group",
                        "all_members_are_administrators": True
                    },
                    "date": 1748176760,
                    "text": "/start",
                    "entities": [
                        {
                            "offset": 0,
                            "length": 6,
                            "type": "bot_command"
                        }
                    ]
                }
            },
            
            "group_single_audio": {
                "description": "群聊上传单个音频文件",
                "update_id": 123456918,
                "message": {
                    "message_id": 2003,
                    "from": {
                        "id": 111111111,
                        "is_bot": False,
                        "first_name": "TestUser",
                        "last_name": "Demo",
                        "username": "testuser",
                        "language_code": "en"
                    },
                    "chat": {
                        "id": -1001000000002,
                        "title": "Test Group",
                        "type": "group",
                        "all_members_are_administrators": True
                    },
                    "date": 1748177939,
                    "audio": {
                        "duration": 207,
                        "file_name": "group_audio.mp3",
                        "mime_type": "audio/mpeg",
                        "file_id": "AUDIO_FILE_ID_004_GROUP_AUDIO_MP3",
                        "file_unique_id": "AUDIO_UNIQUE_004",
                        "file_size": 8301120
                    }
                }
            },
            
            "group_media_group_part1": {
                "description": "群聊媒体组 - 第1个音频文件",
                "update_id": 123456919,
                "message": {
                    "message_id": 2004,
                    "from": {
                        "id": 111111111,
                        "is_bot": False,
                        "first_name": "TestUser",
                        "last_name": "Demo",
                        "username": "testuser",
                        "language_code": "en"
                    },
                    "chat": {
                        "id": -1001000000002,
                        "title": "Test Group",
                        "type": "group",
                        "all_members_are_administrators": True
                    },
                    "date": 1748178064,
                    "media_group_id": "MEDIA_GROUP_TEST_002",
                    "audio": {
                        "duration": 256,
                        "file_name": "group_album_track_1.mp3",
                        "mime_type": "audio/mpeg",
                        "title": "Group Song 1",
                        "performer": "Group Artist",
                        "thumbnail": {
                            "file_id": "THUMBNAIL_FILE_ID_002",
                            "file_unique_id": "THUMB_UNIQUE_002",
                            "file_size": 38176,
                            "width": 320,
                            "height": 320
                        },
                        "thumb": {
                            "file_id": "THUMBNAIL_FILE_ID_002",
                            "file_unique_id": "THUMB_UNIQUE_002",
                            "file_size": 38176,
                            "width": 320,
                            "height": 320
                        },
                        "file_id": "AUDIO_FILE_ID_005_GROUP_ALBUM_TRACK_1_MP3",
                        "file_unique_id": "AUDIO_UNIQUE_005",
                        "file_size": 10370006
                    }
                }
            },
            
            "group_add_music_reply": {
                "description": "群聊回复音频消息使用 /add_music@bot 命令",
                "update_id": 123456922,
                "message": {
                    "message_id": 2005,
                    "from": {
                        "id": 111111111,
                        "is_bot": False,
                        "first_name": "TestUser",
                        "last_name": "Demo",
                        "username": "testuser",
                        "language_code": "en"
                    },
                    "chat": {
                        "id": -1001000000002,
                        "title": "Test Group",
                        "type": "group",
                        "all_members_are_administrators": True
                    },
                    "date": 1748178327,
                    "reply_to_message": {
                        "message_id": 2004,
                        "from": {
                            "id": 111111111,
                            "is_bot": False,
                            "first_name": "TestUser",
                            "last_name": "Demo",
                            "username": "testuser",
                            "language_code": "en"
                        },
                        "chat": {
                            "id": -1001000000002,
                            "title": "Test Group",
                            "type": "group",
                            "all_members_are_administrators": True
                        },
                        "date": 1748178064,
                        "media_group_id": "MEDIA_GROUP_TEST_002",
                        "audio": {
                            "duration": 268,
                            "file_name": "group_album_track_2.mp3",
                            "mime_type": "audio/mpeg",
                            "title": "Group Song 2",
                            "performer": "Group Artist",
                            "file_id": "AUDIO_FILE_ID_006_GROUP_ALBUM_TRACK_2_MP3",
                            "file_unique_id": "AUDIO_UNIQUE_006",
                            "file_size": 11178135
                        }
                    },
                    "text": "/add_music@vocal_transcribe_bot",
                    "entities": [
                        {
                            "offset": 0,
                            "length": 31,
                            "type": "bot_command"
                        }
                    ]
                }
            },
            
            "group_other_user_add_music": {
                "description": "群聊其他用户回复音频消息使用 /add_music@bot 命令",
                "update_id": 123456923,
                "message": {
                    "message_id": 2006,
                    "from": {
                        "id": 222222222,
                        "is_bot": False,
                        "first_name": "OtherUser",
                        "last_name": "Test",
                        "username": "otheruser"
                    },
                    "chat": {
                        "id": -1001000000002,
                        "title": "Test Group",
                        "type": "group",
                        "all_members_are_administrators": True
                    },
                    "date": 1748187204,
                    "reply_to_message": {
                        "message_id": 2004,
                        "from": {
                            "id": 111111111,
                            "is_bot": False,
                            "first_name": "TestUser",
                            "last_name": "Demo",
                            "username": "testuser",
                            "language_code": "en"
                        },
                        "chat": {
                            "id": -1001000000002,
                            "title": "Test Group",
                            "type": "group",
                            "all_members_are_administrators": True
                        },
                        "date": 1748178064,
                        "media_group_id": "MEDIA_GROUP_TEST_002",
                        "audio": {
                            "duration": 256,
                            "file_name": "group_album_track_1.mp3",
                            "mime_type": "audio/mpeg",
                            "title": "Group Song 1",
                            "performer": "Group Artist",
                            "file_id": "AUDIO_FILE_ID_005_GROUP_ALBUM_TRACK_1_MP3",
                            "file_unique_id": "AUDIO_UNIQUE_005",
                            "file_size": 10370006
                        }
                    },
                    "text": "/add_music@vocal_transcribe_bot",
                    "entities": [
                        {
                            "offset": 0,
                            "length": 31,
                            "type": "bot_command"
                        }
                    ]
                }
            },
            
            "group_forwarded_audio_from_channel": {
                "description": "群聊转发音频（来自频道，document类型）",
                "update_id": 123456926,
                "message": {
                    "message_id": 2007,
                    "from": {
                        "id": 111111111,
                        "is_bot": False,
                        "first_name": "TestUser",
                        "last_name": "Demo",
                        "username": "testuser",
                        "language_code": "en"
                    },
                    "chat": {
                        "id": -1001000000002,
                        "title": "Test Group",
                        "type": "group",
                        "all_members_are_administrators": True
                    },
                    "date": 1748190853,
                    "forward_origin": {
                        "type": "channel",
                        "chat": {
                            "id": -1001000000001,
                            "title": "Music Channel",
                            "username": "music_channel_test",
                            "type": "channel"
                        },
                        "message_id": 91,
                        "date": 1746545001
                    },
                    "forward_from_chat": {
                        "id": -1001000000001,
                        "title": "Music Channel",
                        "username": "music_channel_test",
                        "type": "channel"
                    },
                    "forward_from_message_id": 91,
                    "forward_date": 1746545001,
                    "document": {
                        "file_name": "forwarded_music.mp3",
                        "mime_type": "audio/mpeg",
                        "file_id": "DOC_FILE_ID_002_FORWARDED_MUSIC_MP3",
                        "file_unique_id": "DOC_UNIQUE_002",
                        "file_size": 3287850
                    }
                }
            },
            
            
            # 其他测试用例
            "unknown_command": {
                "description": "未知命令",
                "update_id": 123456790,
                "message": {
                    "message_id": 1010,
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
                    "text": "/unknown_command"
                }
            },
            
            "private_text_message": {
                "description": "私聊普通文本消息",
                "update_id": 123456791,
                "message": {
                    "message_id": 1011,
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
                    "date": 1589912680,
                    "text": "Hello, this is just a regular text message"
                }
            }
        }
    
    def run_single_test(self, test_name: str):
        """运行单个测试用例"""
        if test_name not in self.test_cases:
            print(f"❌ Test case '{test_name}' not found")
            return False
        
        test_case = self.test_cases[test_name]
        message = test_case["message"]
        description = test_case["description"]
        
        print(f"\n{'='*70}")
        print(f"🧪 RUNNING TEST: {test_name}")
        print(f"📝 Description: {description}")
        print(f"{'='*70}")
        
        try:
            # 分类消息
            classification = self.classifier.classify_message(message)
            
            # 处理消息
            self.handler.handle_message(message, classification)
            
            print(f"✅ Test '{test_name}' finishes without exception")
            return True
            
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with error: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试用例"""
        print("🚀 Starting Telegram Message Classification Tests")
        print(f"📊 Total test cases: {len(self.test_cases)}")
        
        passed = 0
        failed = 0
        
        # 按类别分组运行测试
        private_tests = [k for k in self.test_cases.keys() if k.startswith('private_')]
        group_tests = [k for k in self.test_cases.keys() if k.startswith('group_')]
        other_tests = [k for k in self.test_cases.keys() if not (k.startswith('private_') or k.startswith('group_'))]
        
        # 运行私聊测试
        print(f"\n🏠 PRIVATE CHAT TESTS ({len(private_tests)} tests)")
        print("="*70)
        for test_name in private_tests:
            if self.run_single_test(test_name):
                passed += 1
            else:
                failed += 1
        
        # 运行群聊测试
        print(f"\n👥 GROUP CHAT TESTS ({len(group_tests)} tests)")
        print("="*70)
        for test_name in group_tests:
            if self.run_single_test(test_name):
                passed += 1
            else:
                failed += 1
        
        # 运行其他测试
        if other_tests:
            print(f"\n🔧 OTHER TESTS ({len(other_tests)} tests)")
            print("="*70)
            for test_name in other_tests:
                if self.run_single_test(test_name):
                    passed += 1
                else:
                    failed += 1
        
        # 总结报告
        print(f"\n{'='*70}")
        print("📊 TEST SUMMARY")
        print(f"{'='*70}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
        print(f"{'='*70}")
        
        return passed, failed
    
    def run_category_tests(self, category: str):
        """运行特定类别的测试"""
        if category == "private":
            tests = [k for k in self.test_cases.keys() if k.startswith('private_')]
        elif category == "group":
            tests = [k for k in self.test_cases.keys() if k.startswith('group_')]
        elif category == "all":
            return self.run_all_tests()
        else:
            print(f"❌ Unknown category: {category}")
            return 0, 0
        
        print(f"🧪 Running {category.upper()} tests ({len(tests)} tests)")
        
        passed = 0
        failed = 0
        
        for test_name in tests:
            if self.run_single_test(test_name):
                passed += 1
            else:
                failed += 1
        
        print(f"\n📊 {category.upper()} TEST SUMMARY")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%" if (passed+failed) > 0 else "No tests run")
        
        return passed, failed


def main():
    """主函数 - 可以通过命令行参数指定测试类别"""
    tester = TelegramMessageTester()
    
    if len(sys.argv) > 1:
        category = sys.argv[1].lower()
        if category in ["private", "group", "all"]:
            tester.run_category_tests(category)
        else:
            # 运行特定的测试用例
            test_name = sys.argv[1]
            tester.run_single_test(test_name)
    else:
        # 默认运行所有测试
        tester.run_all_tests()


if __name__ == "__main__":
    main() 