import boto3
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError
from config import config


class DatabaseManager:
    """数据库管理器 - 处理所有DynamoDB操作"""
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=config.aws_region)
        self.users_table = self.dynamodb.Table(f"{config.dynamodb_table_prefix}-users")
        self.groups_table = self.dynamodb.Table(f"{config.dynamodb_table_prefix}-groups")
        self.jobs_table = self.dynamodb.Table(f"{config.dynamodb_table_prefix}-transcription-jobs")
    
    # ==================== Users表操作 ====================
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        try:
            response = self.users_table.get_item(Key={'user_id': user_id})
            return response.get('Item')
        except ClientError as e:
            print(f"❌ Error getting user {user_id}: {e}")
            return None
    
    def create_user(self, user_id: str, username: str = None, language: str = 'en') -> bool:
        """创建新用户"""
        try:
            now = int(datetime.now().timestamp())
            
            user_data = {
                'user_id': user_id,
                'status': 'standard-user',  # 默认为普通用户
                'language': language,
                'created_at': now,
                'updated_at': now
            }
            
            if username:
                user_data['username'] = username
            
            self.users_table.put_item(
                Item=user_data,
                ConditionExpression='attribute_not_exists(user_id)'  # 防止重复创建
            )
            
            print(f"✅ User {user_id} created successfully")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                print(f"⚠️ User {user_id} already exists")
                return True
            else:
                print(f"❌ Error creating user {user_id}: {e}")
                return False
    
    def update_user_status(self, user_id: str, status: str) -> bool:
        """更新用户状态"""
        try:
            self.users_table.update_item(
                Key={'user_id': user_id},
                UpdateExpression='SET #status = :status, updated_at = :updated_at',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': status,
                    ':updated_at': int(datetime.now().timestamp())
                }
            )
            
            print(f"✅ User {user_id} status updated to {status}")
            return True
            
        except ClientError as e:
            print(f"❌ Error updating user {user_id} status: {e}")
            return False
    
    def update_user_language(self, user_id: str, language: str) -> bool:
        """更新用户语言偏好"""
        try:
            self.users_table.update_item(
                Key={'user_id': user_id},
                UpdateExpression='SET #lang = :lang, updated_at = :updated_at',
                ExpressionAttributeNames={'#lang': 'language'},
                ExpressionAttributeValues={
                    ':lang': language,
                    ':updated_at': int(datetime.now().timestamp())
                }
            )
            
            print(f"✅ User {user_id} language updated to {language}")
            return True
            
        except ClientError as e:
            print(f"❌ Error updating user {user_id} language: {e}")
            return False
    
    # ==================== Groups表操作 ====================
    
    def get_group(self, group_id: str) -> Optional[Dict[str, Any]]:
        """获取群组信息"""
        try:
            response = self.groups_table.get_item(Key={'group_id': group_id})
            return response.get('Item')
        except ClientError as e:
            print(f"❌ Error getting group {group_id}: {e}")
            return None
    
    def create_group(self, group_id: str, group_type: str, title: str = None) -> bool:
        """创建新群组"""
        try:
            now = int(datetime.now().timestamp())
            
            group_data = {
                'group_id': group_id,
                'status': 'active',
                'group_type': group_type,
                'approval_chat': False,
                'created_at': now,
                'updated_at': now,
                'last_activity': now
            }
            
            if title:
                group_data['title'] = title
            
            self.groups_table.put_item(
                Item=group_data,
                ConditionExpression='attribute_not_exists(group_id)'
            )
            
            print(f"✅ Group {group_id} created successfully")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                print(f"⚠️ Group {group_id} already exists")
                return True
            else:
                print(f"❌ Error creating group {group_id}: {e}")
                return False
    
    def update_group_activity(self, group_id: str) -> bool:
        """更新群组活动时间"""
        try:
            self.groups_table.update_item(
                Key={'group_id': group_id},
                UpdateExpression='SET last_activity = :activity, updated_at = :updated_at',
                ExpressionAttributeValues={
                    ':activity': int(datetime.now().timestamp()),
                    ':updated_at': int(datetime.now().timestamp())
                }
            )
            return True
            
        except ClientError as e:
            print(f"❌ Error updating group {group_id} activity: {e}")
            return False
    
    def get_approval_chat(self) -> Optional[Dict[str, Any]]:
        """获取审批聊天群组"""
        try:
            response = self.groups_table.scan(
                FilterExpression='approval_chat = :approval',
                ExpressionAttributeValues={':approval': True}
            )
            
            items = response.get('Items', [])
            return items[0] if items else None
            
        except ClientError as e:
            print(f"❌ Error getting approval chat: {e}")
            return None
    
    # ==================== TranscriptionJobs表操作 ====================
    
    def get_transcription_job(self, user_id: str, group_id: str) -> Optional[Dict[str, Any]]:
        """获取转录任务"""
        try:
            response = self.jobs_table.get_item(
                Key={
                    'user_id': user_id,
                    'group_id': group_id
                }
            )
            return response.get('Item')
        except ClientError as e:
            print(f"❌ Error getting transcription job: {e}")
            return None
    
    def create_transcription_job(self, user_id: str, group_id: str, audio_files: List[Dict]) -> bool:
        """创建转录任务"""
        try:
            now = int(datetime.now().timestamp())
            ttl = now + (7 * 24 * 3600)  # 7天后过期
            
            job_data = {
                'user_id': user_id,
                'group_id': group_id,
                'job_status': 'pending_files',
                'audio_files': audio_files,
                'created_at': now,
                'updated_at': now,
                'ttl': ttl
            }
            
            self.jobs_table.put_item(Item=job_data)
            
            print(f"✅ Transcription job created for user {user_id} in group {group_id}")
            return True
            
        except ClientError as e:
            print(f"❌ Error creating transcription job: {e}")
            return False
    
    def update_job_status(self, user_id: str, group_id: str, status: str, 
                         job_id: str = None, message_id: int = None) -> bool:
        """更新任务状态"""
        try:
            update_expression = 'SET job_status = :status, updated_at = :updated_at'
            expression_values = {
                ':status': status,
                ':updated_at': int(datetime.now().timestamp())
            }
            
            if job_id:
                update_expression += ', job_id = :job_id'
                expression_values[':job_id'] = job_id
            
            if message_id:
                update_expression += ', message_id = :message_id'
                expression_values[':message_id'] = message_id
            
            self.jobs_table.update_item(
                Key={'user_id': user_id, 'group_id': group_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values
            )
            
            print(f"✅ Job status updated to {status}")
            return True
            
        except ClientError as e:
            print(f"❌ Error updating job status: {e}")
            return False
    
    def add_audio_file(self, user_id: str, group_id: str, audio_file: Dict) -> bool:
        """添加音频文件到任务"""
        try:
            # 如果任务不存在，先创建
            existing_job = self.get_transcription_job(user_id, group_id)
            if not existing_job:
                self.create_transcription_job(user_id, group_id, [audio_file])
                return True
            
            # 更新现有任务
            self.jobs_table.update_item(
                Key={'user_id': user_id, 'group_id': group_id},
                UpdateExpression='SET audio_files = list_append(audio_files, :file), updated_at = :updated_at',
                ExpressionAttributeValues={
                    ':file': [audio_file],
                    ':updated_at': int(datetime.now().timestamp())
                }
            )
            
            print(f"✅ Audio file added to job")
            return True
            
        except ClientError as e:
            print(f"❌ Error adding audio file: {e}")
            return False
    
    def complete_job(self, user_id: str, group_id: str, results: List[Dict], 
                    statistics: Dict) -> bool:
        """完成任务并存储结果"""
        try:
            now = int(datetime.now().timestamp())
            ttl = now + (30 * 24 * 3600)  # 30天后过期
            
            self.jobs_table.update_item(
                Key={'user_id': user_id, 'group_id': group_id},
                UpdateExpression='SET job_status = :status, results = :results, statistics = :stats, updated_at = :updated_at, ttl = :ttl',
                ExpressionAttributeValues={
                    ':status': 'completed',
                    ':results': results,
                    ':stats': statistics,
                    ':updated_at': now,
                    ':ttl': ttl
                }
            )
            
            print(f"✅ Job completed successfully")
            return True
            
        except ClientError as e:
            print(f"❌ Error completing job: {e}")
            return False
    
    def get_pending_jobs(self, status: str = 'processing') -> List[Dict]:
        """获取待处理任务"""
        try:
            response = self.jobs_table.query(
                IndexName='job_status-updated_at-index',
                KeyConditionExpression='job_status = :status',
                ExpressionAttributeValues={':status': status}
            )
            
            return response.get('Items', [])
            
        except ClientError as e:
            print(f"❌ Error getting pending jobs: {e}")
            return []
    
    def delete_job(self, user_id: str, group_id: str) -> bool:
        """删除任务"""
        try:
            self.jobs_table.delete_item(
                Key={'user_id': user_id, 'group_id': group_id}
            )
            
            print(f"✅ Job deleted successfully")
            return True
            
        except ClientError as e:
            print(f"❌ Error deleting job: {e}")
            return False


# 全局数据库管理器实例
db = DatabaseManager() 