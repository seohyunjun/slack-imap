from dotenv import load_dotenv
from pytz import timezone
import imaplib
import os

import html2text

import json
import re
            
from dateutil.parser import parse
import datetime

import string

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

def clean(text):
    return "".join(c if str(c).isalnum() else "_" for c in text)

def genai_transform(text: str, genai: genai, prompt: str="Summarize 20 words the following text: "):
    model = genai.GenerativeModel('gemini-pro')
    prompt = prompt + text
    response = model.generate_content(prompt)
    text = response.text
    # slack block message max length is 255.
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

def get_mail(num, genai):
    result, email_data = server.uid('fetch',num, '(RFC822)')
    raw_email = email_data[0][1]
    message = email.message_from_bytes(raw_email)
    raw_email_str = raw_email.decode('utf-8')

    date = make_header(decode_header(message.get('Date')))
    fr = make_header(decode_header(message.get('From')))
    subject = make_header(decode_header(message.get('Subject')))
    email_message = email.message_from_string(raw_email_str)
    for part in email_message.walk():
        print(part.get_content_type())
        if part.get_content_type() == "text/plain":
            body = part.get_payload(decode=True)
            body = body.decode("utf-8")             # Convert byte to str
            body = body.replace("\r\n", " ")
            text = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', body)
            text2 = text.translate(str.maketrans('', '', string.punctuation))
            body_list = re.sub("[^\\w]", " ",  text2).split()
        elif part.get_content_type() == "text/html":
            # body = body.decode("utf-8")             # Convert byte to str
            body = html2text.html2text(part.__str__())
            # body = body.replace("\r\n", " ")
            # html = open("foobar.html").read()
        else:
            continue
    SendAddress_regex = r'[\w\.-]+@[\w\.-]+'
    SendAddress = re.findall(SendAddress_regex, fr.__str__())
    if SendAddress:
        fr = SendAddress[0]
    else:
        fr = fr.__str__() 
        
    message = genai_transform(f"""{subject.__str__()} {body}""", genai)
    return  f"{date.__str__()} {fr} {message}"


if __name__=='__main__':
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    
    server = imaplib.IMAP4_SSL(IMAP4_SSL, port=PORT)
    server.login(EMAIL, PASSWORD)

    since = datetime.datetime.date(datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%d-%b-%Y')

    check = check_mailbox(server, LABEL)
    if check:
        server.select(LABEL)
        result, data = server.uid('search', None, f'(SINCE {since})')
        id_list = data[0].split()
        email_rev = reversed(id_list)
        email_list = list(email_rev)
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
        summary = ""
        for idx, num in enumerate(email_list):
            mail_text = get_mail(num, genai)
            fields.append({"type": "mrkdwn","text": f"{mail_text}"})
            summary += f"""{idx}. {mail_text}\n"""
            if idx == 7:
                break
        
        fields.append({"type": "mrkdwn","text": genai_transform(summary, genai, prompt="Summarize this email list and translate into korean: ")})
        
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
    
    