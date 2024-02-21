# slack-imap
#### This script sends unread emails to slack in real time.
---
#### (24.2.21) v0.0.1 add workflow 
- cron job
- sending email with attachment 


#### Setting .env file or enroll environment variables in Github Actions Secrets 
``` bash
# Gmail Settings
IMAP4_SSL="imap.gmail.com"
EMAIL="...@gmail.com"
PASSWORD="..."
PORT=993
LABEL="..."
```

#### cron job
``` bash
0 */3 * * 1-5
```
