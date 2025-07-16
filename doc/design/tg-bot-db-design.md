Telegram Bot Database Design
==============================

## 概述

本文档描述了Telegram机器人所需的DynamoDB表结构设计。根据功能需求，我们需要创建3个主要的表来管理用户、群组和转录任务。

## 表结构设计

### 表1: `Users`

用于存储用户信息、权限状态和偏好设置。

**表名**: `Users`
**用途**: 管理所有与机器人交互过的用户，控制权限和个人设置
**主键**:
- **分区键 (Partition Key)**: `user_id` (String) - Telegram用户的唯一ID

**属性 (Attributes)**:
- `user_id` (String): 用户ID，主键
- `status` (String): 用户状态，可选值：
  - `'owner'`: 机器人所有者，拥有所有权限，不限量，使用高级资源池
  - `'admin'`: 管理员，拥有所有权限，不限量，使用高级资源池
  - `'premium-user'`: 高级用户，可以使用转录功能，不限量，使用高级资源池
  - `'standard-user'`: 普通用户，可以使用转录功能，限速限量，不付费情况下使用免费资源池
  - `'blocked'`: 被封禁用户，无法使用任何功能
- `language` (String): 用户的语言偏好，例如 `'en'`, `'zh'`
- `username` (String, 可选): 用户的Telegram用户名，方便管理员查看
- `created_at` (Number): 用户首次与机器人交互的时间戳
- `updated_at` (Number): 用户信息最后更新的时间戳

**索引**:
- 无需额外索引，通过主键 `user_id` 查询即可

---

### 表2: `Groups`

用于存储群组信息和机器人在群组中的状态。

**表名**: `Groups`
**用途**: 管理机器人所在的群组，控制群组级别的权限和设置
**主键**:
- **分区键 (Partition Key)**: `group_id` (String) - Telegram群组的唯一ID

**属性 (Attributes)**:
- `group_id` (String): 群组ID，主键
- `status` (String): 群组状态，可选值：
  - `'active'`: 活跃群组，机器人正常工作
  - `'blocked'`: 被封禁群组，机器人拒绝服务
- `group_type` (String): 群组类型，可选值：
  - `'group'`: 普通群组
  - `'supergroup'`: 超级群组
  - `'channel'`: 频道
- `title` (String, 可选): 群组标题/名称
- `description` (String, 可选): 群组描述
- `member_count` (Number, 可选): 群组成员数量（定期更新）
- `approval_chat` (Boolean): 是否设置为审批聊天群组，默认 `false`，全表只能有一个true, 调用日志等发往此群
- `created_at` (Number): 机器人首次加入群组的时间戳
- `updated_at` (Number): 群组信息最后更新的时间戳
- `last_activity` (Number, 可选): 群组中最后一次活动的时间戳

**索引**:
- **GSI1**: `status-updated_at-index` - 用于按状态查询群组并按更新时间排序
  - 分区键: `status`
  - 排序键: `updated_at`

---

### 表3: `TranscriptionJobs`

用于跟踪从"待办列表"到实际"转录任务"的整个流程。

**表名**: `TranscriptionJobs`
**用途**: 管理每个用户在不同聊天中的转录任务，从待处理列表到最终完成的整个生命周期
**主键**:
- **分区键 (Partition Key)**: `user_id` (String) - 用户的唯一ID
- **排序键 (Sort Key)**: `group_id` (String) - 聊天的唯一ID，私聊使用固定值 `'private'`

**属性 (Attributes)**:
- `user_id` (String): 用户ID，分区键
- `group_id` (String): 聊天ID，排序键
- `job_status` (String): 任务当前的状态，可选值：
  - `'pending_files'`: 用户正在添加文件，尚未确认
  - `'pending_approval'`: 用户不在白名单，等待管理员批准
  - `'ready_to_start'`: 文件已添加完毕，等待用户点击"开始转录"
  - `'processing'`: 任务已发送到后端进行处理
  - `'completed'`: 任务已完成
  - `'failed'`: 任务失败
  - `'cancelled'`: 任务已取消
- `audio_files` (List of Maps): 存储待处理的音频文件信息，例如：
  ```json
  [
    {
      "file_id": "BAADBAADrwADBREAAYag2XT...",
      "file_name": "song.mp3",
      "file_size": 5242880,
      "duration": 180,
      "mime_type": "audio/mpeg"
    }
  ]
  ```
- `job_id` (String, 可选): 当用户点击"开始转录"后生成的唯一任务ID
- `message_id` (Number, 可选): 转录任务消息的ID，用于更新进度
- `statistics` (Map, 可选): 任务完成后存储的统计信息，例如：
  ```json
  {
    "gpu_seconds": 120,
    "audio_seconds": 300,
    "speed_factor": 2.5,
    "processing_time": 180
  }
  ```
- `results` (List of Maps, 可选): 转录结果，例如：
  ```json
  [
    {
      "file_id": "BAADBAADrwADBREAAYag2XT...",
      "transcription": "歌词内容...",
      "format": "lrc",
      "language": "zh"
    }
  ]
  ```
- `error_message` (String, 可选): 任务失败时的错误信息
- `created_at` (Number): 列表创建时的时间戳
- `updated_at` (Number): 列表或任务状态最后更新的时间戳

**索引**:
- **GSI1**: `job_status-updated_at-index` - 用于按状态查询任务并按更新时间排序
  - 分区键: `job_status`
  - 排序键: `updated_at`

---

## 数据访问模式

### 用户相关操作
1. **检查用户权限**: 通过 `user_id` 查询 `Users` 表
2. **用户注册**: 在 `Users` 表中创建新记录
3. **更新用户状态**: 更新 `Users` 表中的 `status` 字段

### 群组相关操作
1. **检查群组状态**: 通过 `group_id` 查询 `Groups` 表
2. **群组加入**: 在 `Groups` 表中创建新记录
3. **群组封禁**: 更新 `Groups` 表中的 `status` 字段为 `'blocked'`
4. **查询所有活跃群组**: 使用 GSI1 按 `status='active'` 查询

### 转录任务相关操作
1. **获取用户待办列表**: 通过 `user_id` 和 `group_id` 查询 `TranscriptionJobs` 表
2. **添加音频文件**: 更新 `TranscriptionJobs` 表中的 `audio_files` 字段
3. **开始转录任务**: 更新 `job_status` 为 `'processing'` 并生成 `job_id`
4. **查询进行中的任务**: 使用 GSI1 按 `job_status='processing'` 查询
5. **任务完成**: 更新 `job_status` 为 `'completed'` 并存储结果

## 数据一致性考虑

1. **原子性操作**: 对于需要同时更新多个字段的操作，使用 DynamoDB 的条件更新确保数据一致性
2. **乐观锁**: 使用 `updated_at` 字段实现乐观锁，防止并发更新冲突
3. **数据清理**: 定期清理已完成超过一定时间的转录任务记录，避免数据无限增长

## 成本优化

1. **TTL设置**: 为 `TranscriptionJobs` 表设置TTL，自动删除过期的已完成任务
2. **按需计费**: 使用 DynamoDB 的按需计费模式，根据实际使用量付费
3. **数据压缩**: 对于大型的 `audio_files` 和 `results` 字段，考虑使用压缩存储 