import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from .GLOBAL import EMAIL as gEMAIL, PASSWORD as gPASSWORD
import requests

def send_mail(receiver_email, subject, plain_message, html_message):
    # Send Email
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = gEMAIL
    message["To"] = receiver_email

    text = plain_message
    html = html_message

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    tries = 10
    while tries > 0:
        try:
            with smtplib.SMTP_SSL("mail.privateemail.com", 465, context=context) as server:
                server.login(gEMAIL, gPASSWORD)
                server.sendmail(gEMAIL, receiver_email, message.as_string())
                print("Mail sent to: " + receiver_email)
        except Exception as e:
            print("Couldn't send mail: ", e)
            time.sleep(5)
            tries -= 1
            continue
        break


# Functionality: Sends API Request
# Description: Makes a request to the given
#              API address and retreives needed data
def api_request(url, payload, special_headers, request_method):
    headers = {
    'Content-Type': 'application/json',
    'Content-Type': 'application/json'
    }
    for header in special_headers:
        headers[header] = special_headers[header]

    response = requests.request(request_method, url, headers=headers, data=payload)
    return response.json()