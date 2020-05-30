# RESPONSES
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.template import loader

# TIME
from django.utils import timezone
import time

# MODELS
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from ..API.models import TwoFactorLogin, User, FAQCategory, Question, Profile, Statistics, \
                         Platform, PlatformCurrency, Wallet, Account, AccountKey, UserRole, \
                         Role, PublicityBanners
from django.contrib.auth import get_user_model

# EMAIL
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# MULTI-PROCESS
from multiprocessing import Process

# GLOBALS
from ..GLOBAL import EMAIL as gEMAIL, PASSWORD as gPASSWORD, STAKE_TOKEN, LEVEL_TITLES
from ..APIS import send_mail, api_request
from ..MESSAGES import RECOVERY_SUBJECT, RECOVERY_TEXT, RECOVERY_HTML, \
                       REGISTER_SUBJECT, REGISTER_TEXT, REGISTER_HTML, \
                       REGISTER_ERROR, REGISTER_SUCCESS, \
                       PASSWORD_RESET_SUCCESS_TITLE, PASSWORD_RESET_SUCCESS_MESSAGE, \
                       PASSWORD_RESET_FAIL_TITLE, PASSWORD_RESET_FAIL_MESSAGE, \
                       ACCOUNT_UNLINK_TITLE_SUCCESS, ACCOUNT_UNLINK_MESSAGE_SUCCESS, \
                       ACCOUNT_UNLINK_TITLE_FAIL, ACCOUNT_UNLINK_MESSAGE_FAIL
from ..METHODS import get_json_data, generate_password

# VALIDATION
from .validator import valid_login, valid_tfa, valid_register, image_size, image_dimensions

# STRING
import string

# RANDOM
import random

import os


# Functionality: User Log Out Function
# Description: If the user is logged in, the function
#              will log him out and redirect to the index 
@login_required
def user_logout(request):
    allowed_methods = ["GET"]
    if not request.user.is_authenticated or request.method not in allowed_methods:
        return HttpResponseRedirect(reverse('index'))

    # Check if user is authenticated to log out
    if request.user.is_authenticated:
        logout(request)
    # Redirect  the user to index
    return HttpResponseRedirect(reverse('index'))


# Functionality: Banner Link Return
# Description: For each screen size and platform, 
#              randomly returns a banner
def get_banners():
    banners = {}
    large = PublicityBanners.objects.filter(imageType="large")
    medium = PublicityBanners.objects.filter(imageType="medium")
    small = PublicityBanners.objects.filter(imageType="small")

    pickLarge = random.randint(0, len(large) - 1)
    pickMedium = random.randint(0, len(medium) - 1)
    pickSmall = random.randint(0, len(small) - 1)

    banners["stake_large"] = large[pickLarge].image.url
    banners["stake_medium"] = medium[pickMedium].image.url
    banners["stake_small"] = small[pickSmall].image.url
    return banners


# Functionality: Index Page
# Description: Returns the index page to the user
def index(request):
    # Load the index template and the context
    template    = loader.get_template('WEB/index.html')
    context     = {"banners": get_banners()}
    # Return the template
    return HttpResponse(template.render(context, request))


# Functionality: Login GET
# Description: Returns the login template
def user_login_template(request):
    # Load the login template and the context
    template    = loader.get_template('registration/login.html')
    context     = {}
    # Return the template
    return HttpResponse(template.render(context, request))


# Functionality: Login Form POST
# Description: Checks if the given data is correct and logs the user in
def user_login_form(request):
    # Get the username, password and 2FA
    params = ["username", "password", "2FA"]
    if not all(param in request.POST for param in params):
        return HttpResponseRedirect(reverse('login'))

    username    = request.POST.get('username')
    password    = request.POST.get('password')
    tfa         = request.POST.get('2FA')

    # Check if the username, password and 2FA are valid
    if not valid_login(username, password):
        return HttpResponseRedirect(reverse('login'))
    
    user = authenticate(username=username, password=password)
    
    if user is None or not valid_tfa(user, tfa):
        return HttpResponseRedirect(reverse('login'))

    # Log in the user and clear 2FA codes
    login(request, user)
    TwoFactorLogin.objects.filter(user=user).delete()

    # Redirect the user to the index
    return HttpResponseRedirect(reverse('index'))


# Functionality: Login Page
# Description: If the user is not authenticated, display the 
#              log in page; when the data is sent, process it
#              and log the user. If the user is authenticated
#              then redirect him to the index page.
def user_login(request):
    # If user is authenticated redirect him to index
    allowed_methods = ["POST", "GET"]
    if request.user.is_authenticated or request.method not in allowed_methods:
        return HttpResponseRedirect(reverse('index'))

    if request.method == 'GET':
        return user_login_template(request)
    
    # If the user submitted the login form
    else:
        return user_login_form(request)


# Functionality: Register Form
# Description: Gathers user data, checks if it is valid and
#              registers the user, ending up by returning
#              the context
def user_register_form(request):
    data    = get_json_data(request.POST, ['username', 'email'])
    if len(data) != 2:
        return REGISTER_ERROR

    # Get the username and email
    username    = request.POST.get('username')
    email       = request.POST.get('email')

    # Validate the username and email
    if not valid_register(username, email):
        return REGISTER_ERROR

    # Create a random password
    password = generate_password()

    # Create the registered user
    User.objects.create_user(username, email, password)

    # Send the generated password through email on a different process
    text                = REGISTER_TEXT.format(email, username, password)
    html                = REGISTER_HTML.format(email, username, password)
    send_mail_process   = Process(target=send_mail, args=(email, REGISTER_SUBJECT, text, html))
    send_mail_process.start()
    return REGISTER_SUCCESS


# Functionality: Register Page
# Description: If the user is not authenticated, display the 
#              registration page; when the data is sent, process it,
#              create a password and send it through email. 
#              If the user is authenticated then redirect him to 
#              the index page.
def user_register(request):
    # If user is authenticated redirect him to index
    allowed_methods = ["POST", "GET"]
    if request.user.is_authenticated or request.method not in allowed_methods:
        return HttpResponseRedirect(reverse('index'))

    # Load the register template and the context
    template    = loader.get_template('registration/register.html')
    context     = {}

    # If the user has submitted the register form
    if request.method == 'POST':
        context = user_register_form(request)

    # Return the template
    return HttpResponse(template.render(context, request))


# Functionality: Password Recovery Page
# Description: If the user is not authenticated, redirect him
#              redirect him to the index page. If the request
#              method is GET then display the password recovery
#              page. If the request method is POST, then check
#              if the user's username and email exist and are matching
def recover_password(request):
    allowed_methods = ["POST", "GET"]
    if request.user.is_authenticated or request.method not in allowed_methods:
        return HttpResponseRedirect(reverse('index'))

    if request.method == 'GET':
        return render(request, 'registration/recover_password.html', {})

    fail = {
        'found': 'False',
        'title': PASSWORD_RESET_FAIL_TITLE,
        'message': PASSWORD_RESET_FAIL_MESSAGE,
        'type': 'danger'
    }
    success = {
        'found': 'True',
        'title': PASSWORD_RESET_SUCCESS_TITLE,
        'message': PASSWORD_RESET_SUCCESS_MESSAGE,
        'type': 'success'
    }

    data = get_json_data(request.POST, ['username', 'email'])
    if len(data) != 2:
        return render(request, 'registration/recover_password.html', fail)

    username, email = data
    user = User.objects.filter(username=username, email=email)
    if len(user) > 0:
        return render(request, 'registration/recover_password.html', fail)
        
    user = user.first()
    user.set_password(generate_password())
    user.save()
    send_mail_process = Process(target=send_mail, args=(user.email, user.username, password,))
    send_mail_process.start()
    return render(request, 'registration/recover_password.html', success)


# Functionality: FAQ Page
# Description: Displays all the categories, questions and
#              answers in the FAQ template
def faq(request):
    allowed_methods = ["GET"]
    if request.method not in allowed_methods:
        return HttpResponseRedirect(reverse('index'))

    categories = FAQCategory.objects.all()
    answers = Question.objects.filter(accepted=True)
    context = {"categories": categories, "answers": answers}
    return render(request, 'WEB/faq.html', context)


# Functionality: Terms & Conditions Page
# Description: Displays the terms template
def terms(request):
    allowed_methods = ["GET"]
    if request.method not in allowed_methods:
        return HttpResponseRedirect(reverse('index'))

    context = {}
    return render(request, 'WEB/terms.html', context)


# Functionality: Contact Page
# Description: Displays the contact page
def contact_template(request, context):
    template    = loader.get_template('WEB/contact.html')
    return HttpResponse(template.render(context, request))


# Functionality: Send Contact Mail
# Description: Receives data from user to be sent
#              to the contact email address
def contact_send_mail(request):
    data    = get_json_data(request.POST, ['email', 'subject', 'message'])
    if len(data) != 3:
        return {"error": {"title": "Invalid Data", "message": "Please input an email, subject and message"}}

    # Get the username and email
    email, subject, message = data

    message = email + ": " + message

    # Send the generated password through email on a different process
    send_mail_process   = Process(target=send_mail, args=(os.environ["EMAIL"], "CONTACT FORM: " + subject, message, message))
    send_mail_process.start()
    send_mail_process   = Process(target=send_mail, args=(email, subject, message, message))
    send_mail_process.start()
    return {"success": {"title": "Message sent!", "message": "The message has been sent! <br/>We will try to respond as soon as possible!"}}


# Functionality: Contact Page
# Description: Returns the contact page and gathers form data
def contact(request):
    allowed_methods = ["GET", "POST"]
    if request.method not in allowed_methods:
        return HttpResponseRedirect(reverse('index'))
    if request.method == "GET":
        return contact_template(request, {})
    else:
        context =  contact_send_mail(request)
        return contact_template(request, context)


# Functionality: Dashboard Profile Page
def dashboard(request):
    return HttpResponseRedirect('/dashboard/{}'.format(request.user.username))


# Functionality: Dashboard User Profile Page
# Description: Displays another user's profile page
def dashboard_user(request, username):
    allowed_methods = ["GET"]
    if not request.user.is_authenticated or request.method not in allowed_methods:
        return HttpResponseRedirect(reverse('index'))

    user = get_user_model().objects.filter(username=username).first()

    if not user:
        return HttpResponseRedirect(reverse('dashboard'))

    is_owner = user.username == request.user.username

    profile = Profile.objects.filter(user=user).first()
    statistics = Statistics.objects.filter(profile=profile).first() if profile.publicStats == True or is_owner else None
    
    title = ""
    if profile.publicLevel or is_owner:
        for t in LEVEL_TITLES:
            if LEVEL_TITLES[t][0] <= profile.level and profile.level <= LEVEL_TITLES[t][1]:
                title = t
                break
    userWallets = Wallet.objects.filter(profile=profile)
    platforms = Platform.objects.all()
    for platform in platforms:
        currencies = PlatformCurrency.objects.filter(platform=platform)

    main_role = UserRole.objects.filter(profile=profile, primary=True).first()
    name_color = main_role.role.color
    context = {'profile': profile,
               'statistics': statistics,
               'title': title,
               'platforms': platforms,
               'owner': is_owner,
               'name_color': name_color}
    return render(request, 'dashboard/profile.html', context)


# Functionality: Settings Update Avatar
# Description: Gets the avatar, validates it and updates it
def settings_update_avatar(request, context, profile):
    avatar = request.FILES['newAvatar']

    ok = True
    if image_size(avatar) == 400:
        context["sizeError"] = {'title': 'File too large!', 'message': 'Size should not exceed 3 MiB.'}
        ok = False
    if image_dimensions(avatar) == 400:
        context["dimensionsError"] = {'title': 'Incorrect dimensions!', 'message': 'Image width and height must be equal. \
                                                            The image should be at least 150x150 and not more than 500x500'}
        ok = False

    if ok:
        profile.avatar = avatar
        profile.save()
        context["changedAvatar"] = {"title": "Success!", "message": "The Avatar has been changed successfully!"}
    return context


# Functionality: Settings Update Credentials
# Description: Gathers new mail/password and updates them
def settings_update_credentials(request, context):
    data = get_json_data(request.POST, ('email', 'password', 'newpass', 'newpassconfirm'))
    email, password, newpass, newpassconfirm = data

    error = False
    if not request.user.check_password(password):
        context["passError"] = {"title": "Invalid password", "message": "The given password is not corect!"}
        error = True
    if 0 < len(newpass) and len(newpass) < 6:
        context["newPassError"] = {"title": "Password too weak", "message": "The new password must have at least 6 characters!"}
        error = True
    elif newpass != newpassconfirm:
        context["newPassError"] = {"title": "Incorrect New Password", "message": "The new password doesn't match with the confirmation!"}
        error = True
    elif len(User.objects.filter(email=email)) > 0:
        context["existingMailError"] = {"title": "Existing E-Mail", "message": "The given E-Mail address is already in use by another user!"}
        error = True
    
    if not error:
        if email != request.user.email:
            request.user.email = email
            request.user.save()
            context["changedEmail"] = {"title": "Success!", "message": "The E-Mail has been changed successfully!"}
        if len(newpass) > 0:
            request.user.set_password(newpass)
            request.user.save()
            context["changedPassword"] = {"title": "Success!", "message": "The Password has been changed successfully!"}
    return context


# Functionality: Profile Settings Page
# Description: If the user is not authenticated, redirects
#              the user to the index page. If the method is
#              GET then displays the Profile Settings template
#              If the method is POST then check if the user
#              tried modifying his avatar or password/email.
#              If the modified data is valid, then change it
def settings(request):
    allowed_methods = ["POST", "GET"]
    if not request.user.is_authenticated or request.method not in allowed_methods:
        return HttpResponseRedirect(reverse('index'))

    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()
    context = {'profile': profile,
               'platforms': platforms}

    if request.method == "POST":
        if "updateAvatar" in request.POST:
            context = settings_update_avatar(request, context, profile)
        else:
            context = settings_update_credentials(request, context)
    return render(request, 'settings/settings.html', context)


# Functionality: Privacy Settings Update
# Description: Updates user's privacy settings
def change_privacy(request, profile):
    data = get_json_data(request.POST, ("publicStats", "publicLevel", "publicXP", "publicName"))
    publicStats, publicLevel, publicXP, publicName = data
    profile.publicStats = True if publicStats == "true" else False
    profile.publicLevel = True if publicLevel == "true" else False
    profile.publicXP = True if publicXP == "true" else False
    profile.publicName = True if publicName == "true" else False
    profile.save()


# Functionality: Privacy Settings Page
# Description: If the user is not authenticated, redirects
#              him to the index page. If the method is GET, then
#              displays the privacy template. If the method is
#              POST then get the user's given privacy settings and
#              set them
def privacy(request):
    allowed_methods = ["POST", "GET"]
    if not request.user.is_authenticated or request.method not in allowed_methods:
        return HttpResponseRedirect(reverse('index'))

    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()
    context = {'profile': profile,
               'platforms': platforms}

    if request.method == "POST":
        change_privacy(request, profile)

    return render(request, 'settings/privacy.html', context)


# Functionality: Find User's ID on Stake.com
# Description: Makes a query request to stake api with
#              user's username and finds user's ID
def find_user_id_stake(username):
    import requests
    url = "https://api.stake.com/graphql"
    payload = "{\"query\":\"query {\\n user(name: \\\"" + username + "\\\") {\\n id\\n}\\n}\"}"
    headers = {'x-access-token': STAKE_TOKEN,}
    data = api_request(url, payload, headers, "POST")
    if "data" in data and "user" in data["data"]:
        user = data["data"]["user"]
        if "id" in user:
            return user["id"]
    return None


# Functionality: Send a Message on Stake
# Description: Finds user's ID on Stake and makes
#              a mutation request to send a message to
#              the user
def send_message_stake(account, message):
    userId = find_user_id_stake(account.username)
    if userId is None:
        return None
    else:
        url = "https://api.stake.com/graphql"
        payload = "{\"query\":\"mutation {\\n sendMessage(userId: \\\"" + userId + "\\\", message: \\\"" + message + "\\\") {\\n id}}\"}"
        headers = {'x-access-token': STAKE_TOKEN}
        data = api_request(url, payload, headers, "POST")
        return data


# Functionality: Send User Message
# Description: Checks account's platform and sends
#              a given message on that platform to the
#              given user
def send_message(account, message):
    if account.platform.name == "Stake":
        response = send_message_stake(account, message)
        if response is None:
            return None
        else:
            return response


# Functionality: Remove Linked Account
# Description: Receives the id of the account to be
#              deleted and deltes it from the database
def remove_linked_account(request, context):
    id = request.POST.get('accountId')
    if id:
        account = Account.objects.filter(id=id)
        account.delete()
        context["success"] = {"title": ACCOUNT_UNLINK_TITLE_SUCCESS, "message": ACCOUNT_UNLINK_MESSAGE_SUCCESS}
    else:
        context["danger"] = {"title": ACCOUNT_UNLINK_TITLE_FAIL, "message": ACCOUNT_UNLINK_MESSAGE_FAIL}
    return context


# Functionality: Send token on Stake
# Description: Create a linked account and a key for
#              the account and send the key to that account
#              if the message has been send, the account exists
#              otherwise it doesn't and is being deleted
def send_linked_key(profile, platform, username, context):
    account = Account.objects.create(profile=profile, platform=platform, username=username)
    key = AccountKey.objects.filter(account=account).first()
    message = "Your key is: " + key.key
    response = send_message(account, message)
    if response is None:
        context["danger"] = {"title": "Account doesn't exist!", "message": "The given account doesn't exist on the given platform!"}
        account.delete()
        key.delete()
    else:
        context["success"] = {"title": "Account added successfully!", "message": "The given account has been added! A confirmation \
                                                                    token has been sent on your account. Please make sure that you can \
                                                                    receive private messages on the selected platform. If not, enable them or \
                                                                    add skyBot to your friends list and request the token again!"}
    return context


# Functionality: Confirm Linked Account
# Description: Given a token, check if it exists,
#               if it exists, then activate the account,
#               otherwise, return error
def confirm_linked_account(token):
    key = AccountKey.objects.filter(key=token)
    if len(key) == 1:
        key = key.first()
        key.account.active = True
        key.account.save()
        key.delete()
        context["success"] = {"title": "Account activated successfully!", "message": "The given account has been successfully activated!"}
    else:
        context["danger"] = {"title": "Account wasn't activated", "message": "The given token doesn't correspond to any account!"}
    return context


# Functionality: Linked Accounts Settings Page
# Description: If the user is not authenticated, redirects
#              him to the index page. If the method is get
#              displays the linked template. If the method
#              is post then check if the user wanted to remove
#              an account, add a new one or confirm a token.
#              Removing an account will get the id of the account;
#              Adding a new account will send a message with a token
#              on the given platform to the account; Confirming a
#              token will check the unique token in the database and
#              erase it if matching
def linked(request):
    allowed_methods = ["POST", "GET"]
    if not request.user.is_authenticated or request.method not in allowed_methods:
        return HttpResponseRedirect(reverse('index'))
    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()
    linked = Account.objects.filter(profile=profile)
    context = {'profile': profile, 'linked': linked, 'platforms': platforms}
    if request.method == "POST":
        if 'removeAccount' in request.POST:
            context = remove_linked_account(request, context)
        if 'requestToken' in request.POST:
            username = request.POST.get('accountUsername')
            platformId = request.POST.get('accountPlatform')
            if username and platformId:
                platform = Platform.objects.filter(id=platformId).first()
                if len(Account.objects.filter(profile=profile, platform=platform, username=username)) == 0:
                    context = send_linked_key(profile, platform, username, context)
                elif not Account.objects.filter(profile=profile, platform=platform, username=username).first().active:
                    context = send_linked_key(profile, platform, username, context)
                else:
                    context["danger"] = {"title": "Account already activated", "message": "The given account has already been activated on your account!"}
        if 'addAccount' in request.POST:
            token = request.POST.get('accountToken')
            context = confirm_linked_account(token, context)
    return render(request, 'settings/linked.html', context)