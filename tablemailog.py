import argparse
import os
import smtplib

from email import encoders
from email.mime.multipart import MIMEMultipart 
from email.mime.base import MIMEBase
from email.utils import formatdate


DIR = os.path.abspath(os.path.dirname(__file__))

LOGS = [
    os.path.join(DIR, 'tableErrorMGMT.log'),
    os.path.join(DIR, 'Table.log')
]

def send_logs(host, user, password, send_to, send_from, client):
    """
    Sends the log file to send_to
    """
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Subject'] = '{} Logs'.format(client)
    msg['Date'] = formatdate(localtime=True)

    for log in LOGS:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(open(log, 'rb').read())
            encoders.encode_base64(part)
            part.add_header(
                    'Content-Disposition',
                    'attachment; filename={}'.format(os.path.basename(log))
            )
            msg.attach(part)

    try:
            server = smtplib.SMTP(host, 587)
            server.starttls()
            server.login(user, password)
    except Exception as e:
        err = 'Something terrible happened: {}'.format(str(e))
        print (err)
        return False

    try:
        worked = server.sendmail(send_from, send_to, msg.as_string())
    except Exception as e:
        err = 'Unable to send email: {}'.format(str(e))
        print (err)
        return False
    finally:
            server.close()
    return True

def clean_logs():
    """
    Clear out the log files
    """
    for log in LOGS:
        os.remove(log)

def main():
    host = 'smtp.gmail.com'
    user= 'toptiercuisineja@gmail.com'
    password= 't0Pt1eRJ@'
    toAddr= 'ejon.thomasa@gmail.com'
    fromAddr= user
    subject= 'Top Tier Ja- Customer MGMT'

    email_sent = send_logs(host, user, password, toAddr, fromAddr, subject)
    if email_sent:
            clean_logs()

if __name__ == '__main__':
        main()