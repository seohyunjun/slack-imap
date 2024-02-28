from dotenv import load_dotenv
from pytz import timezone
import imaplib
import os

import json
import re
            
from dateutil.parser import parse
import datetime

import email
from email.header import decode_header, make_header

import google.generativeai as genai

load_dotenv()

EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
IMAP4_SSL = os.getenv('IMAP4_SSL')
PORT = os.getenv('PORT')
LABEL = os.getenv('LABEL')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

def genai_transform(text):
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = "Summarize 20 words the following text: " + text
        response = model.generate_content(prompt)
        text = response.text
        # slack block message max length is 255.
        return text[:210]
    except:
        return text[:210]

# INBOX 메일함 선택
def check_mailbox(server, mailbox):
    state, boxes = server.list()
    if state=="OK":
        if LABEL in [box.decode().split(' "/" ')[1].replace("\"","") for box in boxes]:
            print('Mailbox found')
            return "Mailbox found"
        else:
            return "Can't find the mailbox"
    
    else:
        return "Can't connect to the mailbox"

def get_mail(no):
    rv, fetched = server.fetch(no, '(RFC822)')
    message = email.message_from_bytes(fetched[0][1])

    date = make_header(decode_header(message.get('Date')))
    fr = make_header(decode_header(message.get('From')))
    subject = make_header(decode_header(message.get('Subject')))

    if message.is_multipart():
        for part in message.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))
            # if ctype == 'text/plain' and 'attachment' not in cdispo:
            #     body = part.get_payload(decode=True)
            #     break
    else:
        body = message.get_payload(decode=True)
        
    body = body.decode('utf-8') 
    
    SendAddress_regex = r'[\w\.-]+@[\w\.-]+'
    SendAddress = re.findall(SendAddress_regex, fr.__str__())
    if SendAddress:
        fr = SendAddress[0]
    else:
        fr = fr.__str__() 
    message = genai_transform(f"{subject.__str__()} {body}")
    return  f"{date.__str__()} {fr} {message}"


if __name__=='__main__':
    
    server = imaplib.IMAP4_SSL(IMAP4_SSL, port=PORT)
    server.login(EMAIL, PASSWORD)

    since = datetime.datetime.date(datetime.datetime.now()).strftime('%d-%b-%Y')

    check = check_mailbox(server, LABEL)
    if check:
        server.select(LABEL)
        result, data = server.uid('search', None, f'(SINCE {since})')
    else:
        # return Fail slack message
        pass
    
    fields = [
                {
                    "type": "mrkdwn",
                    "text": "*email*" 
                }
            ]
    if result=="OK":
        
        message = ""
        for num in data[0].split():
            mail_text = get_mail(num)
            print(mail_text)
            fields.append({"type": "mrkdwn","text": f"{mail_text}"})
            fields.append({"type": "divider"})
        temp = {
              "text": "Unread Email",
              "blocks": [
                {
                  "type": "section",
                  "fields": fields
                }
              ]
            }
        with open('send_email.json', 'w') as outfile:
            json.dump(temp, outfile, indent=4)
    
    