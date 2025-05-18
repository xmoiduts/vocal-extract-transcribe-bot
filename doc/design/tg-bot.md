Telegram Bot
======

# runs on:
- AWS Lambda
- AWS DynamoDB
- AWS S3
- Computing resources, any of the following:
  - AWS batch EC2 (GPU preferred)
  - AWS Fargate (CPU only)
  - RunPod (GPU preferred)

# needs:
- Telegram Bot API key
- webhook address

# interaction:
- private chat:  
  - /start [msg, keyboard]
    - replies a "start message"
  - sends a message including 1 or more audio file(s)
    - adds all audio files to the new transcription to-do list
    - replies: a "transcription to-do list message"
  - replies to a message with an audio file, with any msg, exmaple: '.'
    - adds the audio file to the new transcription to-do list
    - replies: a "transcription to-do list message"
  - /help [msg, keyboard]
    - replies: a "help message"
  - /mylist [msg, keyboard]
    - replies: a "transcription to-do list message"
    
- group chat:
  - @bot
    - replies: = private chat /start
  - @bot replying to a msg containing 1 or more audio file(s)
    - replies: = private chat "replies to a message with an audio file, with any msg"
    - add audio to:
      - transcription to-do list of the {user $\times$ group}
  - @bot mylist
    - replies: = private chat /mylist, but only shows the {user $\times$ group} list

- approval private chat/group:
  - needs: admin account for every msg
    - /send_approval_here
      - set the group as the approval chat group
    

- no inline mode, any invoker should add this bot to their group first

# internal data structure:

- There should be a privellege control to every interactive action. i.e. who can do {this action}

- "transcription to-do list"
  - for: every {user $\times$ group} there will be a standalone list
  - stored in DynamoDB
  - content:
    - user_id: str
    - group_id: str
    - audio_file_links: list of str
  - one table for the entire bot, one record for each {user $\times$ group}, private chat's `group` value is `private`

- user list
  - stored in DynamoDB
  - content:
    - user_id: str
    - status: [admin, user, blocked]
  - other accounts not in the userlist will need a manual approval to launch a new transcription job

- transcription to-do list message
  - content:
    - text field: this user's audio files yet to be added to the new transcription job
    - optional text field: if the user is not in the userlist, the text will be: "you are not in the userlist, this transcription list is for preview only"
    - button field:
      - only the {user $\times$ group} + admin (if in the group) can operate the buttons
      - "start transcription": click to start a new transcription job
      - "cancel": click to checkout all audio files
      - list of index(int) of audio files, each index is a button, click to remove the audio file from the new transcription job and edit the "transcription to-do list message" to the new status

- transcription job message
  - content:
    - ref to the "transcription to-do list message"
    - text field: "transcription job {job_id} is started", progress: {progress_status}

- transcription job statistics message
  - content:
    - text field: 
      - "transcription job {job_id} is finished"
      - record of the transcription job: audio file names
      - optional: statistics of the transcription job: GPU seconds, audio seconds, speed-factor.
    - once finishes, delete the ref msg and update result

- transcription job outcome message(s)
  - one message for each audio file
  - content: the cc of an audio file
    - text field: 
      - ref to the transcription job statistics message
      - inline cc txt (typically an LRC)

- "approval message"
  - happens:
    - when an account not in the userlist creates a transcription to-do list via both private and group chats
  - content:
    - text field: "user {user_id} wants to start a new transcription job"
    - button field:
      - "approve": click to add the account to the userlist
      - "reject": click to reject the request
