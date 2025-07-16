# DynamoDB 数据库使用说明

> [!WARNING]
>
> Vibe coding generated this file, not validated, I don't know what AI wrote.

## 概述

本项目使用DynamoDB作为数据存储，提供了完整的表创建和数据操作功能。

## 文件结构

- `db_init.py` - 数据库表初始化脚本
- `database.py` - 数据库操作类
- `setup_database.py` - 完整的设置和测试脚本
- `../doc/design/tg-bot-db-design.md` - 详细的数据库设计文档

```txt

      +-------------------------+
      |    setup_database.py    |
      +-------------------------+
           /             \
          /               \
         v                 v
+----------------+   +-----------------+
|   db_init.py   |   |   database.py   |
+----------------+   +-----------------+

```


## 使用方法

### 1. 程序化创建表格（推荐）

```bash
# 设置环境变量
export AWS_REGION=us-east-1
export DYNAMODB_TABLE_NAME=vocal-transcribe-prod
export TELEGRAM_BOT_TOKEN=your_bot_token
export TELEGRAM_BOT_USERNAME=your_bot_username

# 运行设置脚本
python setup_database.py
```

### 2. 在代码中使用数据库

```python
from database import db

# 用户操作
user = db.get_user("123456789")
if not user:
    db.create_user("123456789", "username", "zh")

# 群组操作
db.create_group("-1001234567890", "supergroup", "My Group")

# 转录任务操作
audio_files = [{"file_id": "...", "file_name": "song.mp3", ...}]
db.create_transcription_job("123456789", "-1001234567890", audio_files)
```

### 3. 其他创建方式

#### 使用AWS CLI

```bash
# 创建用户表
aws dynamodb create-table \
    --table-name vocal-transcribe-prod-users \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST

# 创建群组表
aws dynamodb create-table \
    --table-name vocal-transcribe-prod-groups \
    --attribute-definitions \
        AttributeName=group_id,AttributeType=S \
        AttributeName=status,AttributeType=S \
        AttributeName=updated_at,AttributeType=N \
    --key-schema \
        AttributeName=group_id,KeyType=HASH \
    --global-secondary-indexes \
        '[{
            "IndexName": "status-updated_at-index",
            "KeySchema": [
                {"AttributeName": "status", "KeyType": "HASH"},
                {"AttributeName": "updated_at", "KeyType": "RANGE"}
            ],
            "Projection": {"ProjectionType": "ALL"}
        }]' \
    --billing-mode PAY_PER_REQUEST

# 创建转录任务表
aws dynamodb create-table \
    --table-name vocal-transcribe-prod-transcription-jobs \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
        AttributeName=group_id,AttributeType=S \
        AttributeName=job_status,AttributeType=S \
        AttributeName=updated_at,AttributeType=N \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
        AttributeName=group_id,KeyType=RANGE \
    --global-secondary-indexes \
        '[{
            "IndexName": "job_status-updated_at-index",
            "KeySchema": [
                {"AttributeName": "job_status", "KeyType": "HASH"},
                {"AttributeName": "updated_at", "KeyType": "RANGE"}
            ],
            "Projection": {"ProjectionType": "ALL"}
        }]' \
    --billing-mode PAY_PER_REQUEST
```

#### 使用Terraform

```hcl
resource "aws_dynamodb_table" "users" {
  name           = "vocal-transcribe-prod-users"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "user_id"

  attribute {
    name = "user_id"
    type = "S"
  }

  tags = {
    Name = "Vocal Transcribe Users"
  }
}

resource "aws_dynamodb_table" "groups" {
  name           = "vocal-transcribe-prod-groups"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "group_id"

  attribute {
    name = "group_id"
    type = "S"
  }

  attribute {
    name = "status"
    type = "S"
  }

  attribute {
    name = "updated_at"
    type = "N"
  }

  global_secondary_index {
    name            = "status-updated_at-index"
    hash_key        = "status"
    range_key       = "updated_at"
    projection_type = "ALL"
  }

  tags = {
    Name = "Vocal Transcribe Groups"
  }
}

resource "aws_dynamodb_table" "transcription_jobs" {
  name           = "vocal-transcribe-prod-transcription-jobs"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "user_id"
  range_key      = "group_id"

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "group_id"
    type = "S"
  }

  attribute {
    name = "job_status"
    type = "S"
  }

  attribute {
    name = "updated_at"
    type = "N"
  }

  global_secondary_index {
    name            = "job_status-updated_at-index"
    hash_key        = "job_status"
    range_key       = "updated_at"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = {
    Name = "Vocal Transcribe Jobs"
  }
}
```

## 环境变量

必需的环境变量：

- `AWS_REGION` - AWS区域（默认：us-east-1）
- `DYNAMODB_TABLE_NAME` - 表名前缀（默认：vocal-transcribe-tasks）
- `TELEGRAM_BOT_TOKEN` - Telegram机器人令牌
- `TELEGRAM_BOT_USERNAME` - Telegram机器人用户名

## 权限配置

Lambda函数需要以下DynamoDB权限：

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Query",
                "dynamodb:Scan"
            ],
            "Resource": [
                "arn:aws:dynamodb:*:*:table/vocal-transcribe-*",
                "arn:aws:dynamodb:*:*:table/vocal-transcribe-*/index/*"
            ]
        }
    ]
}
```

## 数据结构

### Users表
- `user_id` (String, 主键): 用户ID
- `status` (String): 用户状态（owner/admin/premium-user/standard-user/blocked）
- `language` (String): 语言偏好
- `username` (String): 用户名
- `created_at` (Number): 创建时间
- `updated_at` (Number): 更新时间

### Groups表
- `group_id` (String, 主键): 群组ID
- `status` (String): 群组状态（active/blocked）
- `group_type` (String): 群组类型（group/supergroup/channel）
- `title` (String): 群组标题
- `approval_chat` (Boolean): 是否为审批群组
- `created_at` (Number): 创建时间
- `updated_at` (Number): 更新时间

### TranscriptionJobs表
- `user_id` (String, 分区键): 用户ID
- `group_id` (String, 排序键): 群组ID
- `job_status` (String): 任务状态
- `audio_files` (List): 音频文件列表
- `job_id` (String): 任务ID
- `results` (List): 转录结果
- `statistics` (Map): 统计信息
- `created_at` (Number): 创建时间
- `updated_at` (Number): 更新时间
- `ttl` (Number): 过期时间

## 常见问题

### Q: 表已存在时怎么办？
A: 脚本会自动检测表是否存在，如果存在则跳过创建。

### Q: 如何删除表？
A: 使用AWS控制台或CLI：
```bash
aws dynamodb delete-table --table-name vocal-transcribe-prod-users
```

### Q: 如何查看表内容？
A: 使用AWS控制台或CLI：
```bash
aws dynamodb scan --table-name vocal-transcribe-prod-users
```

### Q: 成本如何？
A: 使用按需计费模式，只有在实际使用时才收费。预估每1000次操作约$0.25。 