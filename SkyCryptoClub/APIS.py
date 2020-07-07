from django.core.mail import send_mail as djMail
import time
from .GLOBAL import EMAIL as gEMAIL, PASSWORD as gPASSWORD
import requests
from .API.models import Languages, Profile

def send_mail(receiver_email, subject, plain_message, html_message):
    # Send Email
    tries = 10
    while tries > 0:
        try:
            djMail(
                subject,
                plain_message,
                gEMAIL,
                [receiver_email],
                fail_silently = False,
                html_message = html_message,
            )
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


def get_user_language(request):
    if request.user.is_authenticated:
        profile = Profile.objects.filter(user=request.user).first()
        language = profile.language
    else:
        language = Languages.objects.filter(name="en").first()
    return language