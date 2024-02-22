from dotenv import load_dotenv
from pytz import timezone
import imaplib
import os

from dateutil.parser import parse
import datetime

import email
from email.header import decode_header, make_header


load_dotenv()

EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
IMAP4_SSL = os.getenv('IMAP4_SSL')
PORT = os.getenv('PORT')
LABEL = os.getenv('LABEL')


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
        pass
        #body = message.get_payload(decode=True)
        
    #body = body.decode('utf-8')
    print(f"{date.__str__()}")
    print(f"Send: {fr}")
    print(f"Title: {subject}")
    
    return f"({date.__str__()}) {fr} {subject}"
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
    
    if result=="OK":
        
        message = ""
        for num in data[0].split():
            
            message+=get_mail(num)+'\t'
            
    print(message.replace('\n','\t'))