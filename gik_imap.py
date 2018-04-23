import imaplib
import smtplib
from string import Template

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import email
from time import sleep
from threading import Thread


ORG_EMAIL = "@gmail.com"
FROM_EMAIL = "gikwebteam" + ORG_EMAIL
FROM_PWD = "p*w4my4*8b6ag6x"
SMTP_SERVER = "imap.gmail.com"
SMTP_PORT = 993


#setup smtp server for sending emails to the respective members
server = smtplib.SMTP(host='smtp.gmail.com', port=587)
server.starttls()
server.login(FROM_EMAIL, FROM_PWD)

#global variables to save names and email from file
names = []
emails = []
len_of_emails = 0
count = 0

# Function to read the contacts from a given contact file and return a
# list of names and email addresses
def get_contacts(filename):

    with open(filename, mode='r', encoding='utf-8') as contacts_file:
        for a_contact in contacts_file:
            names.append(a_contact.split()[0])
            emails.append(a_contact.split()[1])
    return names, emails

def read_template(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

def read_email_from_gmail():
    global count
    try:
        mail = imaplib.IMAP4_SSL(SMTP_SERVER)
        mail.login(FROM_EMAIL, FROM_PWD)
        mail.select('inbox')
        type, data = mail.search(None, 'UnSeen')
        mail_ids = data[0]
        id_list = mail_ids.split()
        if not id_list:
            return
        first_email_id = int(id_list[0])
        latest_email_id = int(id_list[-1])

        for i in range(latest_email_id, first_email_id - 1, -1):
            typ, data = mail.fetch(str(i), '(RFC822)')
            if typ != 'OK':
                print("ERROR getting message")
                return
            for response_part in data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_string(response_part[1].decode("utf-8"))
                    email_subject = msg['subject']
                    email_from = msg['from']
                    print(email_from)
                    print(email_subject)
                    send_email(count, email_subject)
                    count += 1
                    if count == len_of_emails:
                        count = 0
    except Exception as e:
        print(str(e))


def send_email(id, email_subject):
    name = names[id]
    member_email = emails[id]

    #creates the message
    msg = MIMEMultipart()

    #add in actual person to the message template
    message = message_template.substitute(PERSON_NAME=name.title(), EMAIL_SUBJECT=email_subject)
    #setup parameters for the msg
    msg['From'] = FROM_EMAIL
    print(member_email)
    msg['To'] = member_email
    msg['Subject'] = "This is test"

    #add message template body
    msg.attach(MIMEText(message, 'plain'))

    #send the message via the server set up earlier
    server.send_message(msg)

    del msg


if __name__ == '__main__':
    names, emails = get_contacts('members.txt')
    message_template = read_template('message.txt')
    len_of_emails = len(emails)
    Thread(target = read_email_from_gmail).start()
    while True:
        sleep(20)
        Thread(target = read_email_from_gmail).start()
