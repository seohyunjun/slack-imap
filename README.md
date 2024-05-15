# slack-imap
#### This script sends unread emails to slack in real time.
---
#### (24.5.15) v0.0.3 Deseperate the code (End of free plan) 
- Cloud Billing enabled will be billed for Gemini 1.0 Pro requests

#### (24.2.27) v0.0.2 add workflow 
- gemini summarize
- summarize email

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
GOOGLE_API_KEY="..."
```

#### cron job
``` bash
0 */3 * * 1-5
```
