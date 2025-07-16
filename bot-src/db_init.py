import boto3
import json
from botocore.exceptions import ClientError
from config import config


class DynamoDBInitializer:
    """DynamoDB表初始化器"""
    
    def __init__(self):
        self.dynamodb = boto3.client('dynamodb', region_name=config.aws_region)
    
    def create_users_table(self):
        """创建Users表"""
        table_name = f"{config.dynamodb_table_prefix}-users"
        
        try:
            self.dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': 'user_id',
                        'KeyType': 'HASH'  # 分区键
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'user_id',
                        'AttributeType': 'S'
                    }
                ],
                BillingMode='PAY_PER_REQUEST'  # 按需付费
            )
            
            # 等待表创建完成
            waiter = self.dynamodb.get_waiter('table_exists')
            waiter.wait(TableName=table_name)
            
            print(f"✅ Users table '{table_name}' created successfully")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print(f"⚠️ Users table '{table_name}' already exists")
                return True
            else:
                print(f"❌ Error creating Users table: {e}")
                return False
    
    def create_groups_table(self):
        """创建Groups表"""
        table_name = f"{config.dynamodb_table_prefix}-groups"
        
        try:
            self.dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': 'group_id',
                        'KeyType': 'HASH'  # 分区键
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'group_id',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'status',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'updated_at',
                        'AttributeType': 'N'
                    }
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'status-updated_at-index',
                        'KeySchema': [
                            {
                                'AttributeName': 'status',
                                'KeyType': 'HASH'
                            },
                            {
                                'AttributeName': 'updated_at',
                                'KeyType': 'RANGE'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        }
                    }
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            
            waiter = self.dynamodb.get_waiter('table_exists')
            waiter.wait(TableName=table_name)
            
            print(f"✅ Groups table '{table_name}' created successfully")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print(f"⚠️ Groups table '{table_name}' already exists")
                return True
            else:
                print(f"❌ Error creating Groups table: {e}")
                return False
    
    def create_transcription_jobs_table(self):
        """创建TranscriptionJobs表"""
        table_name = f"{config.dynamodb_table_prefix}-transcription-jobs"
        
        try:
            self.dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': 'user_id',
                        'KeyType': 'HASH'  # 分区键
                    },
                    {
                        'AttributeName': 'group_id',
                        'KeyType': 'RANGE'  # 排序键
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'user_id',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'group_id',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'job_status',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'updated_at',
                        'AttributeType': 'N'
                    }
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'job_status-updated_at-index',
                        'KeySchema': [
                            {
                                'AttributeName': 'job_status',
                                'KeyType': 'HASH'
                            },
                            {
                                'AttributeName': 'updated_at',
                                'KeyType': 'RANGE'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        }
                    }
                ],
                BillingMode='PAY_PER_REQUEST',
                # 设置TTL，自动删除过期的已完成任务
                TimeToLiveSpecification={
                    'AttributeName': 'ttl',
                    'Enabled': True
                }
            )
            
            waiter = self.dynamodb.get_waiter('table_exists')
            waiter.wait(TableName=table_name)
            
            print(f"✅ TranscriptionJobs table '{table_name}' created successfully")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print(f"⚠️ TranscriptionJobs table '{table_name}' already exists")
                return True
            else:
                print(f"❌ Error creating TranscriptionJobs table: {e}")
                return False
    
    def initialize_all_tables(self):
        """初始化所有表"""
        print("🚀 Starting DynamoDB table initialization...")
        
        success_count = 0
        
        if self.create_users_table():
            success_count += 1
        
        if self.create_groups_table():
            success_count += 1
        
        if self.create_transcription_jobs_table():
            success_count += 1
        
        if success_count == 3:
            print("✅ All DynamoDB tables initialized successfully!")
            return True
        else:
            print(f"⚠️ Only {success_count}/3 tables initialized successfully")
            return False
    
    def list_tables(self):
        """列出所有表"""
        try:
            response = self.dynamodb.list_tables()
            tables = response['TableNames']
            
            print(f"📋 Found {len(tables)} DynamoDB tables:")
            for table in tables:
                print(f"  - {table}")
            
            return tables
            
        except ClientError as e:
            print(f"❌ Error listing tables: {e}")
            return []


def main():
    """主函数"""
    initializer = DynamoDBInitializer()
    
    # 显示当前表
    print("Current tables:")
    initializer.list_tables()
    
    # 初始化表
    initializer.initialize_all_tables()
    
    # 再次显示表
    print("\nAfter initialization:")
    initializer.list_tables()


if __name__ == "__main__":
    main() 