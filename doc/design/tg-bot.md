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
    - replies: a "<file_name> has been added, + transcription to-do list summary"
  - replies to a message with an audio file, with any msg, exmaple: '.'
    - adds the audio file to the new transcription to-do list
    - replies: a "<file_name> has been added, + transcription to-do list summary"
  - /remove <int>
    - removes the audio file at index <int> from the new transcription to-do list
    - replies: a "<file_name> has been removed, + transcription to-do list summary"
  - /help [msg, keyboard]
    - replies: a "help message"
  - /myTodoList [msg, keyboard]
    - replies: a "transcription to-do list message"
  - <no /transcribe_now>: it must be launched via a "transcribe all now" button click attached to the "transcription to-do list message", means the to-do list must be inexplicitly seen by the user
  - /setlang [msg, keyboard]
    - replies: a "language selection message"
    
- group chat:
  - /start@bot
    - replies: = private chat /start
  - /add_music@bot replying to a msg containing 1 or more audio file(s)
    - add audio to:
      - transcription to-do list of the {user $\times$ group}
    - replies: = private chat "replies to a message with an audio file, with any msg"
  - /remove@bot <int>: = private chat /remove <int>
  - /myTodoList@bot
    - replies: = private chat /myTodoList, but only shows the {user $\times$ group} list, shows the transcription to-do list message.
  - <no /transcribe_now>: same as private chat

- approval private chat/group:
  - needs: admin or owner account for every msg
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
    - language: [en, zh]
  - other accounts not in the userlist will need a manual approval to launch a new transcription job

- transcription to-do list message
  - content:
    - text field: this user's audio files yet to be added to the new transcription job, with each audio file's name and index
    - optional text field: if the user is not in the userlist, the text will be: "you are not in the userlist, this transcription list is for preview only"
    - button field:
      - only the {user $\times$ group} + admin (if in the group) can operate the buttons
      - "start transcription": click to start a new transcription job
      - "cancel": click to checkout all audio files
      - list of index(int) of audio files, each index is a button, click to remove the audio file from the new transcription job and edit the "transcription to-do list message" to the new status

- "transcription to-do list summary"
  - content:
    - text field: "transcription to-do list summary: <br> <files number> files"
    - button field:
      - myTodoList: click to show the "transcription to-do list message"
      - remove this file: click to remove the audio file from the new transcription to-do list

- transcription job message
  - content:
    - ref to the "transcription to-do list message"
    - text field: "transcription job {job_id} is started", progress: {progress_status}
  - reply to: the "transcription to-do list message"
  - update: regularly update the progress until finished
  - self-destruct: once finished, self-destruct.


- transcription job outcome message(s)
  - one message for each media file
  - content: the cc of an audio file
    - media field: processed vocal stem file
    - text field: 
      - ref to the transcription to-do list message
      - inline cc txt (typically an LRC)

- transcription job statistics message
  - content:
    - text field: 
      - "transcription job {job_id} is finished"
      - record of the transcription job: audio file names
      - optional: statistics of the transcription job: GPU seconds, audio seconds, speed-factor.
    - once finishes, delete the ref msg and update result

- "approval message"
  - happens:
    - when an account not in the userlist creates a transcription to-do list via both private and group chats
  - content:
    - text field: "user {user_id} wants to start a new transcription job"
    - button field:
      - "approve": click to add the account to the userlist
      - "reject": click to reject the request

# locating media file
media file message: having the below field:
```
json.message.[reply_to_message].document.mime_type == "audio/mpeg" # more types?
```
For private chat, media files will be [add]ed to the new transcription to-do list immediately when detected.
For group chat, media files will be [add]ed to the new transcription to-do list after the user replies to the bot with /add_music@bot

When media file is to be [add]ed, the bot will:
- detect media group and try to [add] all files in the group to the new transcription to-do list
  - for each file, the bot will validate the file's size and duration, <where to store limit config?> document file type doesn't have duration, so only file size will be validated.
  - if the file is not valid, the bot will reply to the user with the error message
  - if the file is valid, the bot will add the file to the new transcription to-do list

# time_sequence:

## user happy path:
```txt
# in a private chat:
user: /start
[add file(s): may happen multiple times]
user: sends a message with 1 or more audio files | replies to a message that contains 1 or more audio files | forwards a message that contains 1 or more audio files
bot: <file_name(s)> has been added, + transcription to-do list summary (has a "transcribe todo list" button attached)
[check todo list]
user: /myTodoList
bot: transcription to-do list message
[start transcription]
user: click "transcribe todo list" button
bot: reply to the "transcription to-do list message" with a "transcription job message", regularly update the progress until finished, then self-destruct
bot: sends the transcription job outcome message(s) to the user, each media a (groupped) message, containing: vocal-stem, lyrics
bot: sends the transcription job statistics message to the user
[end]
```