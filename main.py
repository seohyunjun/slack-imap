from dotenv import load_dotenv
from pytz import timezone
import imaplib
import os
import html2text
import time
import json
import re
from dateutil.parser import parse
import datetime
import string
import email
from email.header import decode_header, make_header
import google.generativeai as genai

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
IMAP4_SSL = os.getenv("IMAP4_SSL")
PORT = os.getenv("PORT")
LABEL = os.getenv("LABEL")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


def clean(text):
    return "".join(c if str(c).isalnum() else "_" for c in text)


def genai_transform(
    text: str, genai: genai, prompt: str = "Summarize 30 words the following text: ", max_lenght: int=210
):
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    prompt = prompt + text
    response = model.generate_content(prompt)
    text = response.text
    # slack block message max length is 255.
    return text


def genai_gag(genai: genai)->str:
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    now = datetime.datetime.now(tz=timezone("Asia/Seoul"))
    date_format= "%Y-%m-%d"
    prompt = f"""지금 시간({now:{date_format}})에 맞는 농담이나 재밌는 이야기를 해주세요. 50자 이내로 작성해주세요."""
    response = model.generate_content(prompt)
    time.sleep(4)
    text = response.text
    # slack block message max length is 255.
    return text

# INBOX 메일함 선택
def check_mailbox(server, mailbox):
    state, boxes = server.list()
    if state == "OK":
        if LABEL in [box.decode().split(' "/" ')[1].replace('"', "") for box in boxes]:
            print("Mailbox found")
            return "Mailbox found"
        else:
            return "Can't find the mailbox"

    else:
        return "Can't connect to the mailbox"


def normalize_text(s:str, sep_token = " \n ")->str:
    s = re.sub(r'\s+',  ' ', s).strip()
    s = re.sub(r". ,","",s)
    # remove all instances of multiple spaces
    s = s.replace("..",".")
    s = s.replace(". .",".")
    s = s.replace("\n", "")
    s = s.replace("#","")
    s = s.strip()
    if s =="":
        s = "<blank>"
    return s

def get_mail(num, genai):
    result, email_data = server.uid("fetch", num, "(RFC822)")
    raw_email = email_data[0][1]
    message = email.message_from_bytes(raw_email)
    raw_email_str = raw_email.decode("utf-8")

    date = make_header(decode_header(message.get("Date")))
    fr = make_header(decode_header(message.get("From")))
    subject = make_header(decode_header(message.get("Subject")))
    email_message = email.message_from_string(raw_email_str)
    for part in email_message.walk():
        print(part.get_content_type())
        if part.get_content_type() == "text/plain":
            body = part.get_payload(decode=True)
            body = body.decode("utf-8")  # Convert byte to str
            body = body.replace("\r\n", " ")
            text = re.sub(r"\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*", "", body)
            text2 = text.translate(str.maketrans("", "", string.punctuation))
            body_list = re.sub("[^\\w]", " ", text2).split()
        elif part.get_content_type() == "text/html":
            # body = body.decode("utf-8")             # Convert byte to str
            body = html2text.html2text(part.__str__())
            # body = body.replace("\r\n", " ")
            # html = open("foobar.html").read()
        else:
            continue
    SendAddress_regex = r"[\w\.-]+@[\w\.-]+"
    SendAddress = re.findall(SendAddress_regex, fr.__str__())
    if SendAddress:
        fr = SendAddress[0]
    else:
        fr = fr.__str__()

    message = genai_transform(f"""{subject.__str__()} {body}""", genai)
    return f"{date.__str__()} {fr} {message}"

def preprocess_block(message:str, genai: genai) -> list[dict]:
    """Preprocess the message to fit the slack block message format."""
    try:
        answer = genai_transform(
            normalize_text(message),
            genai,
            prompt="아래 이메일을 요약하고 한국어로 번역 :"
            )
    except Exception as e:
        answer = f"Error: {e}"
        error_block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{answer}",
                }
            }
        return error_block
            
    max_legnth = 255
    block_counts = len(answer) // max_legnth + 1
    blocks = []
    for i in range(block_counts):
        block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{answer[i*max_legnth:(i+1)*max_legnth]}",
                    }
            }
        blocks.append(block)
    return blocks

if __name__ == "__main__":
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    server = imaplib.IMAP4_SSL(IMAP4_SSL, port=PORT)
    server.login(EMAIL, PASSWORD)

    since = datetime.datetime.date(
        datetime.datetime.now() - datetime.timedelta(days=1)
    ).strftime("%d-%b-%Y")

    check = check_mailbox(server, LABEL)
    if check:
        server.select(LABEL)
        result, data = server.uid("search", None, f"(SINCE {since})")
        id_list = data[0].split()
        email_rev = reversed(id_list)
        email_list = list(email_rev)
    else:
        # return Fail slack message
        pass

    fields = [{"type": "mrkdwn", "text": "*email*"}]
    if result == "OK":
        message = ""
        summary = ""
        for idx, num in enumerate(email_list):
            mail_text = get_mail(num, genai)
            fields.append({"type": "mrkdwn", "text": f"{mail_text}"})
            summary += f"""{idx}. {mail_text}\n"""
        
        block=[]
        block.append({"type": "section", "fields": fields})
        block.append({"type": "divider"})
        
        for info_block in preprocess_block(summary, genai):
            block.append(info_block)
            
        temp = {"text": "Unread Email","blocks": block}
        
        with open("send_email.json", "w") as outfile:
            json.dump(temp, outfile, indent=4)