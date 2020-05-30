from django.contrib.auth import get_user_model
from ..API.models import TwoFactorLogin
from django.core.files.images import get_image_dimensions

from django.utils import timezone
import time
import string
import re

# Functionality: Check Username and Password
def valid_login(username, password):
    # Username and Password must be string and have 
    # at least 1 character each
    if type(username) != str or type(password) != str:
        return False
    if len(username) == 0 or len(password) == 0:
        return False
    
    # The username must correspond to a registered user
    matching_user = get_user_model().objects.filter(username=username)
    if len(matching_user) == 0:
        return False

    # The password must match with the account
    user = matching_user.first()
    return user.check_password(password)

# Functionality: Check 2FA Token
def valid_tfa(user, tfa):
    # TFA must be a string with at least 1 chracter
    if type(tfa) != str or len(tfa) == 0:
        return False
    
    # The 2FA Token must correspond to the given user
    matching_token = TwoFactorLogin.objects.filter(user=user, key=tfa)
    if len(matching_token) == 0:
        return False
    
    # The 2FA Token must not be expired
    token = matching_token.first()
    return timezone.now() < token.valid_until

# Functionality: Check Register Credentials
def valid_register(username, email):
    # The username and password must be string and have
    # at least 1 character
    if type(username) != str or type(email) != str:
        return False
    
    # Username must not contain invalid symbols
    admitted_symbols = string.ascii_letters + string.digits + "._"
    check_username = re.sub('[{}]'.format(admitted_symbols), '', username)
    print(check_username)
    if len(check_username) != 0:
        return False
    
    # The username and email must not be used by any other account
    matching_usernames = get_user_model().objects.filter(username=username)
    matching_emails    = get_user_model().objects.filter(email=email)
    return len(matching_usernames) + len(matching_emails) == 0


# Functionality: Validate Image Size
# Description: Checks if the image size is under
#              the specified limit
# Data input: 
# Data output: 
def image_size(value):
    limit = 3 * 1024 * 1024
    if value.size > limit:
        return 400
    return 200


# Functionality: Validate Image Dimensions
# Description: Checks if the image is between the
#              minimum and maximum dimensions with
#              equal length and height
def image_dimensions(value):
    minLength = 150
    maxLength = 500
    width, height = get_image_dimensions(value)
    if width != height or width < minLength or width > maxLength:
        return 400
    return 200