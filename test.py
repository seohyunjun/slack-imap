# https://docs.python.org/ko/3/library/imaplib.html
import imaplib

imap = imaplib.IMAP4_SSL('imap.gmail.com')

server = imaplib.IMAP4_SSL('imap.gmail.com', port=993)
server.login('bnmy6581@gmail.com', 'sbpmfonacwxiqati')


# INBOX 메일함 선택
server.select(mailbox='INBOX')



from datetime import datetime
since = datetime.strftime(datetime.now(), '%d-%b-%Y %H:%M:%S')
since = datetime.strftime(datetime.now(), 'DD-Mmm-YYYY HH:MM:SS +HHMM')

result, data = server.uid('search', '(SINCE "'+since+'")', 'UNSEEN')
typ, data = server.search(None, 'ALL')

mail_index = data[0].split()
for num in mail_index[-10:]:
    typ, data = server.fetch(num, '(RFC822)')
    print('Message %s\n%s\n' % (num, data[0][1]))
server.close()



def print_mail(data):
    raw_readable = data[0][1].decode('utf-8')
    print(raw_readable)

print_mail(data)
############################################
import imaplib
import email
from email.header import decode_header

# account credentials
username = "bnmy6581@gmail.com"
password = "sbpmfonacwxiqati"

# create an IMAP4 class with SSL 
imap = imaplib.IMAP4_SSL("imap.gmail.com")
# authenticate
imap.login(username, password)

status, messages = imap.select("INBOX")
# number of top emails to fetch
N = 3
# total number of emails
messages = int(messages[0])

for i in range(messages, messages-N, -1):
    # fetch the email message by ID
    res, msg = imap.fetch(str(i), "(RFC822)")
    for response in msg:
        if isinstance(response, tuple):
            # parse a bytes email into a message object
            msg = email.message_from_bytes(response[1])
            date = decode_header(msg["Date"])[0][0]
            print(date)
            
import datetime
date = (datetime.date.today() - datetime.timedelta(1)).strftime("%d-%b-%Y")
date = "17-Feb-2024"
(_, data) = server.search(None, ('UNSEEN'), '(SENTSINCE {0})'.format(date))
#.format("someone@yahoo.com".strip()))

ids = data[0].split()


for id in ids:
    res, msg = server.fetch(id, '(RFC822)')
    for response in msg:
        if isinstance(response, tuple):
            # parse a bytes email into a message object
            msg = email.message_from_bytes(response[1])
            date = decode_header(msg["Date"])[0][0]
            
            print(date)
            print(msg.get_all('subject'))

# Delivered-To:
# Received:
# X-Google-Smtp-Source:
# X-Received:
# ARC-Seal:
# ARC-Message-Signature:
# ARC-Authentication-Results:
# Return-Path:
# Received:
# Received-SPF:
# Authentication-Results:
# DKIM-Signature:
# DKIM-Signature:
# X-Gm-Message-State:
# X-Google-Smtp-Source:
# MIME-Version:
# From:
# Date:
# Message-ID:
# Subject:
# To:
# Content-Type:
# Bcc:
# X-Original-To:

msg['Bcc']



###

import time
from itertools import chain
import email
import imaplib
import base64
import os
import re
import datetime
date = (datetime.date.today() - datetime.timedelta(1)).strftime("%d-%b-%Y")
date = "17-Feb-2024"

imap_ssl_host = 'imap.gmail.com'
imap_ssl_port = 993
username = 'bnmy6581@gmail.com'
password = 'sbpmfonacwxiqati'

# imap = imaplib.IMAP4_SSL('imap.gmail.com')

# server = imaplib.IMAP4_SSL('imap.gmail.com', port=993)
# server.login('bnmy6581@gmail.com', 'sbpmfonacwxiqati')


# if need to restrict mail search.
criteria = {}
uid_max = 0

def search_string(uid_max, criteria):
    c = list(map(lambda t: (t[0], '"'+str(t[1])+'"'), criteria.items())) + [('UID', '%d:*' % (uid_max+1))]
    return '(%s)' % ' '.join(chain(*c))
    # Produce search string in IMAP format:
    #   e.g. (FROM "me@gmail.com" SUBJECT "abcde" BODY "123456789" UID 9999:*)
#Get any attachemt related to the new mail

#Getting the uid_max, only new email are process

#login to the imap
mail = imaplib.IMAP4_SSL(imap_ssl_host)
mail.login(username, password)
#select the folder
mail.select('inbox')

import datetime
date = (datetime.date.today() - datetime.timedelta(1)).strftime("%d-%b-%Y")

result, data = mail.search(None, ('UNSEEN'), '(SENTSINCE {0})'.format(date))
result, data = mail.uid('SEARCH', None, search_string(uid_max, criteria))
uids = [int(s) for s in data[0].split()]

if uids:
    uid_max = max(uids)
    # Initialize `uid_max`. Any UID less than or equal to `uid_max` will be ignored subsequently.
#Logout before running the while loop
print(uid_max)
mail.logout()
while 1:
    mail = imaplib.IMAP4_SSL(imap_ssl_host)
    mail.login(username, password)
    mail.select('inbox')
    result, data = mail.uid('search', None, search_string(uid_max, criteria))
    uids = [int(s) for s in data[0].split()]

    for uid in uids:
        # Have to check again because Gmail sometimes does not obey UID criterion.
        if uid > uid_max:
            result, data = mail.uid('fetch', str(uid), '(RFC822)')
            for response_part in data:
                if isinstance(response_part, tuple):
                    #message_from_string can also be use here
                    print(email.message_from_bytes(response_part[1])) #processing the email here for whatever
            uid_max = uid
mail.logout()
time.sleep(1)

# define gmail search function and get the latest email and print the email
def gmail_search():
    mail = imaplib.IMAP4_SSL(imap_ssl_host)
    mail.login(username, password)
    mail.select('inbox')
    result, data = mail.uid('search', None, "ALL")
    inbox_item = data[0].split()
    most_recent = inbox_item[-1]
    result2, email_data = mail.uid('fetch', most_recent, '(RFC822)')
    raw_email = email_data[0][1].decode("utf-8")
    # preprocess the email and print the email title and content
    email_message = email.message_from_string(raw_email)
    print(email_message['To'])
    print(email_message['From'])
    print(email_message['Subject'])
    print(email_message.get_payload())
    
    
    print(email_message)
    mail.logout()
    
# imaplib에서 기본 메일만 가져오기
import imaplib
import email
import os
import datetime
import time
import base64
import re

# 사용자 설정 기본값
imap_ssl_host = 'imap.gmail.com'


#####
from dateutil.parser import parse
import datetime

import imaplib
import email
from email.header import decode_header, make_header

server = imaplib.IMAP4_SSL('imap.gmail.com')
server.login(username, password)

print(server.list()[1])

rv, data = server.select('Receipts')
recent_no = data[0]

rv, fetched = server.fetch(recent_no, '(RFC822)')
message = email.message_from_bytes(fetched[0][1])

date = make_header(decode_header(message.get('Date')))
fr = make_header(decode_header(message.get('From')))
subject = make_header(decode_header(message.get('Subject')))

if message.is_multipart():
    for part in message.walk():
        ctype = part.get_content_type()
        cdispo = str(part.get('Content-Disposition'))
        if ctype == 'text/plain' and 'attachment' not in cdispo:
            body = part.get_payload(decode=True)
            break
else:
    body = message.get_payload(decode=True)

body = body.decode('utf-8')

# load module for timezone
from pytz import timezone
# convert AS KST

print(f"{date.__str__()}")
print(f"보낸사람:{fr}")
print(f"제목:{subject}")
print(f"내용:{body}")

server.close()
server.logout()
