# RESPONSES
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.template import loader

# TIME
from django.utils import timezone
import time

# MODELS
from django.contrib.auth import authenticate, login, logout
from ..API.models import TwoFactorLogin, User, FAQCategory, Question, Profile, \
                         Platform, PlatformCurrency, Wallet, Account, UserRole, \
                         Role, PublicityBanners, Exchange, Currency, ExchangeStatus, ExchangeTaxPeer, \
                         SupportTicket, SupportTicketMessage, SupportCategory
from django.contrib.auth import get_user_model

# DJANGO DECORATORS
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

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

from decimal import *
import math


# Functionality: Banner Link Return
# Description: For each screen size and platform, 
#              randomly returns a banner
def get_banners():
    banners = {}
    large = PublicityBanners.objects.filter(imageType="large")
    medium = PublicityBanners.objects.filter(imageType="medium")
    small = PublicityBanners.objects.filter(imageType="small")

    if len(large) > 0:
        pickLarge = random.randint(0, len(large) - 1)
        banners["stake_large"] = large[pickLarge].image.url
    if len(medium) > 0:
        pickMedium = random.randint(0, len(medium) - 1)
        banners["stake_medium"] = medium[pickMedium].image.url
    if len(small) > 0:
        pickSmall = random.randint(0, len(small) - 1)
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
@require_http_methods(["GET", "POST"])
def user_login(request):
    # If user is authenticated redirect him to index
    if request.user.is_authenticated:
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
@require_http_methods(["GET", "POST"])
def user_register(request):
    # If user is authenticated redirect him to index
    if request.user.is_authenticateds:
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
@require_http_methods(["GET", "POST"])
def recover_password(request):
    if request.user.is_authenticated:
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
    if len(user) < 1:
        return render(request, 'registration/recover_password.html', fail)
        
    user = user.first()
    password = generate_password()
    user.set_password(password)
    user.save()
    send_mail_process = Process(target=send_mail, args=(user.email, user.username, password, password))
    send_mail_process.start()
    return render(request, 'registration/recover_password.html', success)


# Functionality: FAQ Page
# Description: Displays all the categories, questions and
#              answers in the FAQ template
@require_http_methods(["GET"])
def faq(request):

    categories = FAQCategory.objects.all()
    answers = Question.objects.filter(accepted=True)
    context = {"categories": categories, "answers": answers}
    return render(request, 'WEB/faq.html', context)


# Functionality: Terms & Conditions Page
# Description: Displays the terms template
@require_http_methods(["GET"])
def terms(request):
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
@require_http_methods(["GET", "POST"])
def contact(request):
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
@login_required
@require_http_methods(["GET"])
def dashboard_user(request, username):

    user = get_user_model().objects.filter(username=username).first()

    if not user:
        return HttpResponseRedirect(reverse('dashboard'))

    is_owner = user.username == request.user.username

    profile = Profile.objects.filter(user=user).first()
    statistics = {}
    statistics["totalExchangesStarted"] = len(Exchange.objects.filter(creator=profile))
    statistics["totalExchanges"] = len(Exchange.objects.filter(exchanged_by=profile))
    
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
@login_required
@require_http_methods(["GET", "POST"])
def settings(request):

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
@login_required
@require_http_methods(["GET", "POST"])
def privacy(request):

    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()
    context = {'profile': profile,
               'platforms': platforms}

    if request.method == "POST":
        change_privacy(request, profile)

    return render(request, 'settings/privacy.html', context)


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


# Functionality: Find User's ID on Stake.com
# Description: Makes a query request to stake api with
#              user's username and finds user's ID
def find_user(api):
    import requests
    url = "https://api.stake.com/graphql"
    payload = "{\"query\":\"query {\\n user {\\n name\\n}\\n}\"}"
    headers = {'x-access-token': api,}
    data = api_request(url, payload, headers, "POST")
    user = data["data"]["user"]
    if user:
        return user["name"]
    return None


# Functionality: Confirm Linked Account
# Description: Check if the given account is
#              paired to the API Key and create
#              the account
def confirm_linked_account(request, context):
    data = get_json_data(request.POST, ("accountUsername", "accountPlatform", "apiKey"))
    username, platform, key = data
    account = Account.objects.filter(username=username)
    if len(account) == 0:
        if find_user(key) == username:
            platform = Platform.objects.filter(id=platform).first()
            profile = Profile.objects.filter(user=request.user).first()
            Account.objects.create(username=username, platform=platform, profile=profile, active=True)
            context["success"] = {"title": "Account linked successfully!", "message": "The given account has been successfully linked!"}
        else:
            context["danger"] = {"title": "Account wasn't linked", "message": "The given API Key doesn't match the provided username!"}
    else:
        context["danger"] = {"title": "Account wasn't linked", "message": "The given account is already linked!"}
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
@login_required
@require_http_methods(["GET", "POST"])
def linked(request):
    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()
    linked = Account.objects.filter(profile=profile)
    context = {'profile': profile, 'linked': linked, 'platforms': platforms}
    if request.method == "POST":
        if 'removeAccount' in request.POST:
            context = remove_linked_account(request, context)
        if 'addAccount' in request.POST:
            context = confirm_linked_account(request, context)
    return render(request, 'settings/linked.html', context)

    
@login_required
@require_http_methods(["GET", "POST"])
def requestExchange(request):
    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()
    context = {'profile': profile, 'platforms': platforms, "emptyTableMessage": "There are no opened Exchange Requests", "exchanges": exchanges}
    if request.method == "POST":
        getcontext().prec = 20
        data = get_json_data(request.POST, ("requestFrom", "fromPlatform", "fromCurrency", "fromAmount", "toPlatform", "toCurrency", "toAmount"))
        peer, fromPlatform, fromCurrency, fromAmount, toPlatform, toCurrency, toAmount = data
        fcurrency = Currency.objects.filter(name=fromCurrency).first()
        tcurrency = Currency.objects.filter(name=toCurrency).first()

        creator = Profile.objects.filter(user=request.user).first()

        fromPlatform = Platform.objects.filter(id=fromPlatform).first()
        fromCurrency = PlatformCurrency.objects.filter(platform=fromPlatform, currency=fcurrency).first()
        fromAmount = Decimal(fromAmount)

        creatorWallet = Wallet.objects.filter(profile=creator, store=fromCurrency).first()
        if creatorWallet.amount < fromAmount:
            context['insufficient'] = {"title": "Insufficient funds!"}
            return render(request, 'exchange/exchange_request.html', context)
        else:
            creatorWallet.amount -= fromAmount
            creatorWallet.save()

        toPlatform = Platform.objects.filter(id=toPlatform).first()
        toCurrency = PlatformCurrency.objects.filter(platform=toPlatform, currency=tcurrency).first()
        toAmount = Decimal(toAmount)

        ratio = toAmount / fromAmount
        status = ExchangeStatus.objects.filter(status="Pending").first()

        if peer == "user":
            taxCreator = ExchangeTaxPeer.objects.filter(currency=fcurrency).filter(minAmount__lte=fromAmount).filter(maxAmount__gte=fromAmount).first()
            taxExchanger = ExchangeTaxPeer.objects.filter(currency=tcurrency).filter(minAmount__lte=toAmount).filter(maxAmount__gte=toAmount).first()
        
        creatorAmount = (Decimal(1) - taxCreator.percentage / Decimal(100)) * toAmount
        exchangerAmount = (Decimal(1) - taxExchanger.percentage / Decimal(100)) * fromAmount

        exchange = Exchange.objects.create(creator=creator, from_currency=fromCurrency, from_amount=fromAmount,
                                to_currency=toCurrency, to_amount=toAmount, ratio=ratio, status=status, 
                                creator_amount=creatorAmount, exchanger_amount=exchangerAmount,
                                taxCreator=taxCreator, taxExchanger=taxExchanger)
        return redirect('/exchange/' + str(exchange.eid) + "/")
    return render(request, 'exchange/exchange_request.html', context)


def filterExchanges(request, exchanges):
    # Retrieve GET parameters
    fromPlatform = request.GET["fromPlatform"] if "fromPlatform" in request.GET and request.GET["fromPlatform"] != "" else "any"
    fromCurrency = request.GET["fromCurrency"] if "fromCurrency" in request.GET and request.GET["fromCurrency"] != "" else "any"
    toPlatform = request.GET["toPlatform"] if "toPlatform" in request.GET and request.GET["toPlatform"] != "" else "any"
    toCurrency = request.GET["toCurrency"] if "toCurrency" in request.GET and request.GET["toCurrency"] != "" else "any"
    try:
        minRequested = Decimal(request.GET["minRequested"]) if "minRequested" in request.GET and request.GET["minRequested"] != "" else "any"
    except:
        minRequested = "any"
    try:
        maxRequested = Decimal(request.GET["maxRequested"]) if "maxRequested" in request.GET and request.GET["maxRequested"] != "" else "any"
    except:
        maxRequested = "any"
    try:
        minGiven = Decimal(request.GET["minGiven"]) if "minGiven" in request.GET and request.GET["minGiven"] != "" else "any"
    except:
        minGiven = "any"
    try:
        maxGiven = Decimal(request.GET["maxGiven"]) if "maxGiven" in request.GET and request.GET["maxGiven"] != "" else "any"
    except:
        maxGiven = "any"

    # Filter From Platform and From Currency
    fromPCs = PlatformCurrency.objects.all()
    if fromPlatform != "any":
        platform = Platform.objects.filter(id=fromPlatform).first()
        fromPCs = fromPCs.filter(platform=platform)
    if fromCurrency != "any":
        currency = Currency.objects.filter(name=fromCurrency).first()
        fromPCs = fromPCs.filter(currency=currency)
    filteredFrom = Exchange.objects.none()
    for pc in fromPCs:
        filteredFrom = filteredFrom | exchanges.filter(from_currency = pc)
    exchanges = filteredFrom
    # Filter To Platform and To Currency
    toPCs = PlatformCurrency.objects.all()
    if toPlatform != "any":
        platform = Platform.objects.filter(id=toPlatform).first()
        toPCs = toPCs.filter(platform=platform)
    if toCurrency != "any":
        currency = Currency.objects.filter(name=toCurrency).first()
        toPCs = toPCs.filter(currency=currency)
    filteredFrom = Exchange.objects.none()
    for pc in toPCs:
        filteredFrom = filteredFrom | exchanges.filter(to_currency = pc)
    exchanges = filteredFrom

    # Filter Mins and Maxes
    if minRequested != "any":
        exchanges = exchanges.filter(to_amount__gte=minRequested)
    if maxRequested != "any":
        exchanges = exchanges.filter(to_amount__lte=maxRequested)
    if minGiven != "any":
        exchanges = exchanges.filter(from_amount__gte=minGiven)
    if maxGiven != "any":
        exchanges = exchanges.filter(from_amount__lte=maxGiven)
    return exchanges

    
@login_required
@require_http_methods(["GET"])
def exchanges(request, page):
    if page <= 0:
        return HttpResponseRedirect(reverse('index'))
    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()
    exchanges = Exchange.objects.filter(status="Open")
    exchanges = filterExchanges(request, exchanges)

    # Pagination
    displayPerPage = 30
    totalPages = math.ceil(len(exchanges) / displayPerPage)
    startPagination = max(page - 2, 1) if page < totalPages else 1
    endPagination = min(totalPages, page + 2) + 1
    pages = [i for i in range(startPagination, endPagination)]
    canNext = page < totalPages
    canPrevious = page > 1
    begin = displayPerPage * (page - 1)
    end = displayPerPage * page
    exchanges = exchanges.order_by('-created_at')[begin:end]

    context = {'totalPages': totalPages, 'canPrevious': canPrevious, 'canNext': canNext, 
               'currentPage': page, 'pages': pages, 'profile': profile, 'platforms': platforms, 
               "emptyTableMessage": "There are no opened Exchange Requests", "exchanges": exchanges}
    return render(request, 'exchange/exchanges_list.html', context)


def exchanges_history(request, page):
    return HttpResponseRedirect('/exchanges/history/{}/page={}/'.format(request.user.username, page))
    

@login_required
@require_http_methods(["GET", "POST"])
def exchanges_history_user(request, username, page):
    if not request.user.username == username or page <= 0:
        return HttpResponseRedirect(reverse('index'))
    user = get_user_model().objects.filter(username=username).first()
    profile = Profile.objects.filter(user=user).first()
    platforms = Platform.objects.all()
    exchanges = Exchange.objects.filter(creator=profile) | Exchange.objects.filter(exchanged_by=profile)

    exchanges = filterExchanges(request, exchanges)

    # Pagination
    displayPerPage = 30
    totalPages = math.ceil(len(exchanges) / displayPerPage)
    startPagination = max(page - 2, 1) if page < totalPages else 1
    endPagination = min(totalPages, page + 2) + 1
    pages = [i for i in range(startPagination, endPagination)]
    canNext = page < totalPages
    canPrevious = page > 1
    begin = displayPerPage * (page - 1)
    end = displayPerPage * page
    exchanges = exchanges.order_by('-created_at')[begin:end]

    context = {'totalPages': totalPages, 'canPrevious': canPrevious, 'canNext': canNext, 
               'currentPage': page, 'pages': pages, 'profile': profile, 'platforms': platforms, 
               "emptyTableMessage": "You have no exchanges in your history", "exchanges": exchanges}
    return render(request, 'exchange/exchanges_history.html', context)

    
@login_required
@require_http_methods(["GET"])
def exchange_page(request, exchange_id):
    exchange = Exchange.objects.filter(eid=exchange_id).first()

    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()
    context = {'profile': profile, 'platforms': platforms, "exchange": exchange}
    return render(request, 'exchange/exchange.html', context)

  
@login_required
@require_http_methods(["GET"])
def support(request):

    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()

    tickets = SupportTicket.objects.filter(creator=profile).order_by('-created_at')

    context = {'profile': profile, 'platforms': platforms, 'tickets': tickets}
    return render(request, 'support/contact_support.html', context)

    
@login_required
@require_http_methods(["GET"])
def ticket(request, tid):

    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()

    ticket = SupportTicket.objects.filter(ticketId=tid).first()
    messages = SupportTicketMessage.objects.filter(ticket=ticket)

    context = {'profile': profile, 'platforms': platforms, 'ticket': ticket, 'messages': messages}
    return render(request, 'support/ticket.html', context)

    
@login_required
@require_http_methods(["GET", "POST"])
def createTicket(request):
    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()
    categories = SupportCategory.objects.all().order_by('order')
    context = {'profile': profile, 'platforms': platforms, 'categories': categories}

    if request.method == "POST":
        if "title" not in request.POST:
            context["titleError"] = {"title": "Please input a title!", "message": ""}
            return render(request, 'support/create_ticket.html', context)
        if not (8 < len(request.POST["title"]) and len(request.POST["title"]) < 60):
            context["titleError"] = {"title": "Title length error!", "message": "Please give a suggestive title with no more than 60 characters!"}
            return render(request, 'support/create_ticket.html', context)
        if "category" not in request.POST or request.POST["category"] == "":
            context["categoryError"] = {"title": "Please choose a category!", "message": "The category should match your problem, if no category is appropiate, choose \"Others\"."}
            return render(request, 'support/create_ticket.html', context)
        if not SupportCategory.objects.filter(order=request.POST["category"]).first():
            context["categoryError"] = {"title": "Please choose a valid category!", "message": "The category should match your problem, if no category is appropiate, choose \"Others\"."}
            return render(request, 'support/create_ticket.html', context)
        if "message" not in request.POST:
            context["messageError"] = {"title": "Please input a message!", "message": "The message should describe your problem as detailed as possible."}
            return render(request, 'support/create_ticket.html', context)
        if len(request.POST["message"]) < 10:
            context["messageError"] = {"title": "Please input a more detailed message!", "message": "The message should describe your problem as detailed as possible."}
            return render(request, 'support/create_ticket.html', context)
        title = request.POST["title"]
        category = SupportCategory.objects.filter(order=request.POST["category"]).first()
        message = request.POST["message"]
        creator = profile
        ticket = SupportTicket.objects.create(creator=creator, title=title, category=category)
        SupportTicketMessage.objects.create(ticket=ticket, sender=creator, message=message)
        return redirect('/support/ticket/' + str(ticket.ticketId) + "/")

    return render(request, 'support/create_ticket.html', context)