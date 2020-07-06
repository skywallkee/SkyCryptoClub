from django.contrib.auth import get_user_model
from ..API.models import TwoFactorLogin, User, FAQCategory, Question, Profile, \
                         Platform, PlatformCurrency, Wallet, Account, UserRole, \
                         Role, PublicityBanners, Exchange, Currency, ExchangeStatus, ExchangeTaxPeer, \
                         SupportTicket, SupportTicketMessage, SupportCategory
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.files.images import get_image_dimensions
from ..API.views import get_user_language
from ..MESSAGES import MESSAGES
from django.utils import timezone
import time
import string
import re

# /login/ VALIDATORS



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
    if type(username) != str or type(email) != str or username == "" or email == "":
        return False
    try:
        validate_email(email)
    except ValidationError:
        return False
    
    # Username must not contain invalid symbols
    admitted_symbols = string.ascii_letters + string.digits + "._"
    check_username = re.sub('[{}]'.format(admitted_symbols), '', username)
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
def valid_image_size(value):
    limit = 3 * 1024 * 1024
    if value.size > limit:
        return False
    return True


# Functionality: Validate Image Dimensions
# Description: Checks if the image is between the
#              minimum and maximum dimensions with
#              equal length and height
def valid_file_dimensions(value):
    minLength = 150
    maxLength = 500
    width, height = get_image_dimensions(value)
    if width != height or width < minLength or width > maxLength:
        return False
    return True


def get_settings_update_errors(request, email, password, newpass, newpassconfirm):
    errors = []
    if not request.user.check_password(password):
        errors.append(MESSAGES[get_user_language(request).name]["PASSWORD"]["FAIL"]["INCORRECT"])
    if 0 < len(newpass) and len(newpass) < 6:
        errors.append(MESSAGES[get_user_language(request).name]["PASSWORD"]["FAIL"]["SHORT"])
    elif newpass != newpassconfirm:
        errors.append(MESSAGES[get_user_language(request).name]["PASSWORD"]["FAIL"]["NOT_MATCHING"])
    if len(User.objects.filter(email=email)) > 0 and User.objects.filter(email=email).first() != request.user:
        errors.append(MESSAGES[get_user_language(request).name]["EMAIL"]["FAIL"]["EXISTING"])
    return errors


def get_settings_update_avatar_errors(request, avatar):
    errors = []
    if not valid_image_size(avatar):
        errors.append(MESSAGES[get_user_language(request).name]["AVATAR"]["FAIL"]["LARGE_IMAGE"])
    if not valid_file_dimensions(avatar):
        errors.append(MESSAGES[get_user_language(request).name]["AVATAR"]["FAIL"]["DIMENSIONS"])
    return errors


def get_support_create_errors(request):
    errors = []
    if "title" not in request.POST:
        errors.append(MESSAGES[get_user_language(request).name]["CREATE_TICKET"]["FAIL"]["MISSING_TITLE"])
    elif not (8 < len(request.POST["title"]) and len(request.POST["title"]) < 60):
        errors.append(MESSAGES[get_user_language(request).name]["CREATE_TICKET"]["FAIL"]["TITLE_LENGTH"])
    if "category" not in request.POST or request.POST["category"] == "":
        errors.append(MESSAGES[get_user_language(request).name]["CREATE_TICKET"]["FAIL"]["MISSING_CATEGORY"])
    elif not SupportCategory.objects.filter(order=request.POST["category"]).first():
        errors.append(MESSAGES[get_user_language(request).name]["CREATE_TICKET"]["FAIL"]["INVALID_CATEGORY"])
    if "message" not in request.POST:
        errors.append(MESSAGES[get_user_language(request).name]["CREATE_TICKET"]["FAIL"]["MISSING_MESSAGE"])
    elif len(request.POST["message"]) < 10:
        errors.append(MESSAGES[get_user_language(request).name]["CREATE_TICKET"]["FAIL"]["SHORT_MESSAGE"])
    return errors