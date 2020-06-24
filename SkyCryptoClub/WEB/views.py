from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.template import loader
from django.utils import timezone
import time
from django.contrib.auth import authenticate, login, logout
from ..API.models import TwoFactorLogin, User, FAQCategory, Question, Profile, \
                         Platform, PlatformCurrency, Wallet, Account, UserRole, \
                         Role, PublicityBanners, Exchange, Currency, ExchangeStatus, ExchangeTaxPeer, \
                         SupportTicket, SupportTicketMessage, SupportCategory
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from multiprocessing import Process
from ..GLOBAL import EMAIL as gEMAIL, PASSWORD as gPASSWORD, STAKE_TOKEN, LEVEL_TITLES
from ..APIS import send_mail, api_request
from ..MESSAGES import MESSAGES
from ..METHODS import get_json_data, generate_password
from ..API.views import get_user_language
from .validator import valid_login, valid_tfa, valid_register, get_settings_update_errors, \
                       get_settings_update_avatar_errors, get_support_create_errors
import string
import random
import os
from decimal import *
import math


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


def index(request):
    template    = loader.get_template('WEB/index.html')
    context     = {"banners": get_banners()}
    return HttpResponse(template.render(context, request))


def user_login_template(request):
    template    = loader.get_template('registration/login.html')
    context     = {}
    return HttpResponse(template.render(context, request))


def user_login_form(request):
    data    = get_json_data(request.POST, ["username", "password", "2FA"])
    if len(data) != 3:
        return HttpResponseRedirect(reverse('login'))

    username, password, tfa = data

    if not valid_login(username, password):
        return HttpResponseRedirect(reverse('login'))
    
    user = authenticate(username=username, password=password)

    if user is None or not valid_tfa(user, tfa):
        return HttpResponseRedirect(reverse('login'))

    login(request, user)
    try:
        TwoFactorLogin.objects.filter(user=user).delete()
    except:
        pass

    return HttpResponseRedirect(reverse('index'))


@require_http_methods(["GET", "POST"])
def user_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))

    if request.method == 'GET':
        return user_login_template(request)
    else:
        return user_login_form(request)


def user_register_form(request):
    data    = get_json_data(request.POST, ['username', 'email'])
    if len(data) != 2:
        return {"messages": [MESSAGES[get_user_language(request)]["REGISTER"]["FAIL"]]}

    username, email = data

    if not valid_register(username, email):
        return {"messages": [MESSAGES[get_user_language(request).name]["REGISTER"]["FAIL"]]}

    password = generate_password()
    User.objects.create_user(username, email, password)

    subject             = MESSAGES[get_user_language(request).name]["REGISTER_MAIL"]["SUBJECT"]
    text                = MESSAGES[get_user_language(request).name]["REGISTER_MAIL"]["MESSAGE"].format(email, username, password)
    html                = MESSAGES[get_user_language(request).name]["REGISTER_MAIL"]["HTML"].format(email, username, password)
    send_mail_process   = Process(target=send_mail, args=(email, subject, text, html))
    send_mail_process.start()
    return {"messages": [MESSAGES[get_user_language(request).name]["REGISTER"]["SUCCESS"]]}


@require_http_methods(["GET", "POST"])
def user_register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    template    = loader.get_template('registration/register.html')
    context     = {}
    if request.method == 'POST':
        context = user_register_form(request)
    return HttpResponse(template.render(context, request))


@require_http_methods(["GET", "POST"])
def recover_password(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))

    if request.method == 'GET':
        return render(request, 'registration/recover_password.html', {})

    data = get_json_data(request.POST, ['username', 'email'])
    if len(data) != 2:
        return render(request, 'registration/recover_password.html', {"messages": [MESSAGES[get_user_language(request).name]["PASSWORD_RESET"]["FAIL"]]})

    username, email = data
    user = User.objects.filter(username=username, email=email).first()
    if user is None:
        return render(request, 'registration/recover_password.html', {"messages": [MESSAGES[get_user_language(request).name]["PASSWORD_RESET"]["FAIL"]]})

    password = generate_password()
    user.set_password(password)
    user.save()
    subject = MESSAGES[get_user_language(request).name]["RECOVERY_MAIL"]["SUBJECT"]
    text = MESSAGES[get_user_language(request).name]["RECOVERY_MAIL"]["MESSAGE"].format(user.email, user.username, user.password)
    html = MESSAGES[get_user_language(request).name]["RECOVERY_MAIL"]["HTML"].format(user.email, user.username, user.password)
    send_mail_process = Process(target=send_mail, args=(user.email, subject, text, html))
    send_mail_process.start()
    return render(request, 'registration/recover_password.html', {"messages": [MESSAGES[get_user_language(request).name]["PASSWORD_RESET"]["SUCCESS"]]})


@require_http_methods(["GET"])
def faq(request):
    categories = FAQCategory.objects.all()
    answers = Question.objects.filter(accepted=True)
    context = {"categories": categories, "answers": answers}
    return render(request, 'WEB/faq.html', context)


@require_http_methods(["GET"])
def terms(request):
    context = {}
    return render(request, 'WEB/terms.html', context)


def contact_template(request, context):
    template    = loader.get_template('WEB/contact.html')
    return HttpResponse(template.render(context, request))


def contact_send_mail(request):
    data    = get_json_data(request.POST, ['email', 'subject', 'message'])
    if len(data) != 3:
        return {"messages": [MESSAGES[get_user_language(request).name]["CONTACT_US"]["FAIL"]]}

    email, subject, message = data

    message = email + ": " + message

    send_mail_process   = Process(target=send_mail, args=(os.environ["EMAIL"], "CONTACT FORM: " + subject, message, message))
    send_mail_process.start()
    send_mail_process   = Process(target=send_mail, args=(email, subject, message, message))
    send_mail_process.start()
    return {"messages": [MESSAGES[get_user_language(request).name]["CONTACT_US"]["SUCCESS"]]}


@require_http_methods(["GET", "POST"])
def contact(request):
    if request.method == "GET":
        return contact_template(request, {})

    context =  contact_send_mail(request)
    return contact_template(request, context)

@login_required
@require_http_methods(["GET"])
def dashboard(request):
    return HttpResponseRedirect('/dashboard/{}'.format(request.user.username))


@login_required
@require_http_methods(["GET"])
def dashboard_user(request, username):
    user = get_user_model().objects.filter(username=username).first()

    if user is None:
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
    name_color = "#000000"
    if main_role is not None:
        name_color = main_role.role.color
    context = {'profile': profile,
               'statistics': statistics,
               'title': title,
               'platforms': platforms,
               'owner': is_owner,
               'name_color': name_color}
    return render(request, 'dashboard/profile.html', context)


def settings_update_avatar(request, context, profile):
    if 'newAvatar' not in request.FILES:
        return context["messages"].append(MESSAGES[get_user_language(request).name]["AVATAR"]["FAIL"]["NO_IMAGE"])
    avatar = request.FILES['newAvatar']
    context["messages"] = get_settings_update_avatar_errors(avatar)

    if len(context["messages"]) == 0:
        profile.avatar = avatar
        profile.save()
        context["messages"].append(MESSAGES[get_user_language(request).name]["AVATAR"]["SUCCESS"])
    return context


def settings_update_credentials(request, context):
    data = get_json_data(request.POST, ('email', 'password', 'newpass', 'newpassconfirm'))
    if len(data) != 4:
        return context
    email, password, newpass, newpassconfirm = data

    context["messages"] = get_settings_update_errors(request, email, password, newpass, newpassconfirm)
    
    if len(context["messages"]) == 0:
        if email != request.user.email:
            request.user.email = email
            request.user.save()
            context["messages"].append(MESSAGES[get_user_language(request).name]["EMAIL"]["SUCCESS"])
        if len(newpass) > 0:
            request.user.set_password(newpass)
            request.user.save()
            context["messages"].append(MESSAGES[get_user_language(request).name]["PASSWORD"]["SUCCESS"])
    return context


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


def change_privacy(request, profile):
    data = get_json_data(request.POST, ("publicStats", "publicLevel", "publicXP", "publicName"))
    publicStats, publicLevel, publicXP, publicName = data
    profile.publicStats = publicStats == "true"
    profile.publicLevel = publicLevel == "true"
    profile.publicXP = publicXP == "true"
    profile.publicName = publicName == "true"
    profile.save()
    return [MESSAGES[get_user_language(request).name]["PRIVACY"]["SUCCESS"]]


@login_required
@require_http_methods(["GET", "POST"])
def privacy(request):
    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()
    context = {'profile': profile,
               'platforms': platforms}

    if request.method == "POST":
        context["messages"] = change_privacy(request, profile)

    return render(request, 'settings/privacy.html', context)


def remove_linked_account(request, context):
    if "accountId" not in request.POST:
        context["messages"] = [MESSAGES[get_user_language(request).name]["ACCOUNT_UNLINK"]["FAIL"]]
    id = request.POST.get('accountId')
    account = Account.objects.filter(id=id)
    if account is None:
        context["messages"] = [MESSAGES[get_user_language(request).name]["ACCOUNT_UNLINK"]["FAIL"]]
    try:
        account.delete()
        context["messages"] = [MESSAGES[get_user_language(request).name]["ACCOUNT_UNLINK"]["SUCCESS"]]
    except:
        context["messages"] = [MESSAGES[get_user_language(request).name]["ACCOUNT_UNLINK"]["FAIL"]]
    return context


def find_user_stake(api):
    import requests
    url = "https://api.stake.com/graphql"
    payload = "{\"query\":\"query {\\n user {\\n name\\n}\\n}\"}"
    headers = {'x-access-token': api,}
    data = api_request(url, payload, headers, "POST")
    if "data" not in data:
        return None
    if "user" not in data["data"]:
        return None
    if "name" not in data["data"]["user"]:
        return None
    return data["data"]["user"]["name"]


def confirm_stake_account(request, username, key, platform)
    if find_user_stake(key) == username:
        profile = Profile.objects.filter(user=request.user).first()
        Account.objects.create(username=username, platform=platform, profile=profile, active=True)
        messages = [MESSAGES[get_user_language(request).name]["ACCOUNT_LINK"]["SUCCESS"]]
    else:
        messages = [MESSAGES[get_user_language(request).name]["ACCOUNT_LINK"]["FAIL"]["INVALID_API"]]
    return messages


def confirm_linked_account(request, context):
    data = get_json_data(request.POST, ("accountUsername", "accountPlatform", "apiKey"))
    if len(data) != 3:
        context["messages"] = [MESSAGES[get_user_language(request).name]["ACCOUNT_LINK"]["FAIL"]["INVALID_API"]]
        return context
    username, platform, key = data
    account = Account.objects.filter(username=username).first()
    if account is not None:
        context["messages"] = [MESSAGES[get_user_language(request).name]["ACCOUNT_LINK"]["FAIL"]["ALREADY_LINKED"]]
        return context
    
    platform = Platform.objects.filter(id=platform).first()
    if platform is None:
        context["messages"] = [MESSAGES[get_user_language(request).name]["ACCOUNT_LINK"]["FAIL"]["INVALID_API"]]
        return context

    if platform.name == "Stake":
        context["messages"] = confirm_stake_account(request, username, key, platform)
    return context


@login_required
@require_http_methods(["GET", "POST"])
def linked(request):
    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()
    context = {'profile': profile, 'platforms': platforms}
    if request.method == "POST":
        if 'removeAccount' in request.POST:
            context = remove_linked_account(request, context)
        if 'addAccount' in request.POST:
            context = confirm_linked_account(request, context)
    linked = Account.objects.filter(profile=profile)
    context["linked"] = linked
    return render(request, 'settings/linked.html', context)

    
@login_required
@require_http_methods(["GET", "POST"])
def requestExchange(request):
    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()
    context = {'profile': profile, 'platforms': platforms, "emptyTableMessage": MESSAGES[get_user_language(request).name]["EMPTY_EXCHANGE_TABLE"], "exchanges": exchanges}
    if request.method == "POST":
        getcontext().prec = 20
        data = get_json_data(request.POST, ("requestFrom", "fromPlatform", "fromCurrency", "fromAmount", "toPlatform", "toCurrency", "toAmount"))
        if len(data) != 7:
            context["messages"] = [MESSAGES[get_user_language(request).name]["EXCHANGE_REQUEST"]["FAIL"]]
            return render(request, 'exchange/exchange_request.html', context)
        peer, fromPlatform, fromCurrency, fromAmount, toPlatform, toCurrency, toAmount = data
        fcurrency = Currency.objects.filter(name=fromCurrency).first()
        tcurrency = Currency.objects.filter(name=toCurrency).first()
        if fcurrency is None or tcurrency is None:
            context["messages"] = [MESSAGES[get_user_language(request).name]["EXCHANGE_REQUEST"]["FAIL"]]
            return render(request, 'exchange/exchange_request.html', context)

        creator = Profile.objects.filter(user=request.user).first()

        fromPlatform = Platform.objects.filter(id=fromPlatform).first()
        if fromPlatform is None:
            context["messages"] = [MESSAGES[get_user_language(request).name]["EXCHANGE_REQUEST"]["FAIL"]]
            return render(request, 'exchange/exchange_request.html', context)
        fromCurrency = PlatformCurrency.objects.filter(platform=fromPlatform, currency=fcurrency).first()
        if fromCurrency is None:
            context["messages"] = [MESSAGES[get_user_language(request).name]["EXCHANGE_REQUEST"]["FAIL"]]
            return render(request, 'exchange/exchange_request.html', context)
        fromAmount = Decimal(fromAmount)
        if fromAmount <= Decimal(0):
            context["messages"] = [MESSAGES[get_user_language(request).name]["EXCHANGE_REQUEST"]["FAIL"]]
            return render(request, 'exchange/exchange_request.html', context)

        creatorWallet = Wallet.objects.filter(profile=creator, store=fromCurrency).first()
        if creatorWallet is None:
            context["messages"] = [MESSAGES[get_user_language(request).name]["EXCHANGE_REQUEST"]["FAIL"]]
            return render(request, 'exchange/exchange_request.html', context)

        if creatorWallet.amount < fromAmount:
            context["messages"] = [MESSAGES[get_user_language(request).name]["EXCHANGE_REQUEST"]["FAIL"]]
            return render(request, 'exchange/exchange_request.html', context)
        else:
            creatorWallet.amount -= fromAmount
            creatorWallet.save()

        toPlatform = Platform.objects.filter(id=toPlatform).first()
        if toPlatform is None:
            context["messages"] = [MESSAGES[get_user_language(request).name]["EXCHANGE_REQUEST"]["FAIL"]]
            return render(request, 'exchange/exchange_request.html', context)
        toCurrency = PlatformCurrency.objects.filter(platform=toPlatform, currency=tcurrency).first()
        if toCurrency is None:
            context["messages"] = [MESSAGES[get_user_language(request).name]["EXCHANGE_REQUEST"]["FAIL"]]
            return render(request, 'exchange/exchange_request.html', context)
        toAmount = Decimal(toAmount)
        if toAmount <= Decimal(0):
            context["messages"] = [MESSAGES[get_user_language(request).name]["EXCHANGE_REQUEST"]["FAIL"]]
            return render(request, 'exchange/exchange_request.html', context)

        ratio = toAmount / fromAmount
        status = ExchangeStatus.objects.filter(status="Pending").first()
        if peer != "user":
            peer = "user"
        if peer == "user":
            taxCreator = ExchangeTaxPeer.objects.filter(currency=fcurrency).filter(minAmount__lte=fromAmount).filter(maxAmount__gte=fromAmount).first()
            taxExchanger = ExchangeTaxPeer.objects.filter(currency=tcurrency).filter(minAmount__lte=toAmount).filter(maxAmount__gte=toAmount).first()
            if taxCreator is None or taxExchanger is None:
                context["messages"] = [MESSAGES[get_user_language(request).name]["EXCHANGE_REQUEST"]["FAIL"]]
                return render(request, 'exchange/exchange_request.html', context)
        
        creatorAmount = (Decimal(1) - taxExchanger.percentage / Decimal(100)) * toAmount
        exchangerAmount = (Decimal(1) - taxCreator.percentage / Decimal(100)) * fromAmount

        try:
            exchange = Exchange.objects.create(creator=creator, from_currency=fromCurrency, from_amount=fromAmount,
                                                to_currency=toCurrency, to_amount=toAmount, ratio=ratio, status=status, 
                                                creator_amount=creatorAmount, exchanger_amount=exchangerAmount,
                                                taxCreator=taxCreator, taxExchanger=taxExchanger)
        except:
            context["messages"] = [MESSAGES[get_user_language(request).name]["EXCHANGE_REQUEST"]["FAIL"]]
            return render(request, 'exchange/exchange_request.html', context)
        return redirect('/exchange/' + str(exchange.eid) + "/")
    return render(request, 'exchange/exchange_request.html', context)


def filterExchanges(request, exchanges):
    fromPlatform = request.GET["fromPlatform"] if "fromPlatform" in request.GET and request.GET["fromPlatform"] != "" else "any"
    fromCurrency = request.GET["fromCurrency"] if "fromCurrency" in request.GET and request.GET["fromCurrency"] != "" else "any"
    toPlatform = request.GET["toPlatform"] if "toPlatform" in request.GET and request.GET["toPlatform"] != "" else "any"
    toCurrency = request.GET["toCurrency"] if "toCurrency" in request.GET and request.GET["toCurrency"] != "" else "any"
    try:
        minRequested = Decimal(request.GET["minRequested"])
    except:
        minRequested = "any"
    try:
        maxRequested = Decimal(request.GET["maxRequested"])
    except:
        maxRequested = "any"
    try:
        minGiven = Decimal(request.GET["minGiven"])
    except:
        minGiven = "any"
    try:
        maxGiven = Decimal(request.GET["maxGiven"])
    except:
        maxGiven = "any"

    fromPCs = PlatformCurrency.objects.all()
    if fromPlatform != "any":
        platform = Platform.objects.filter(id=fromPlatform).first()
        if platform is not None:
            fromPCs = fromPCs.filter(platform=platform)
    if fromCurrency != "any":
        currency = Currency.objects.filter(name=fromCurrency).first()
        if currency is not None:
            fromPCs = fromPCs.filter(currency=currency)
    filteredFrom = Exchange.objects.none()
    for pc in fromPCs:
        filteredFrom = filteredFrom | exchanges.filter(from_currency = pc)
    toPCs = PlatformCurrency.objects.all()
    if toPlatform != "any":
        platform = Platform.objects.filter(id=toPlatform).first()
        if platform is not None:
            toPCs = toPCs.filter(platform=platform)
    if toCurrency != "any":
        currency = Currency.objects.filter(name=toCurrency).first()
        if currency is not None:
            toPCs = toPCs.filter(currency=currency)
    filteredTo = Exchange.objects.none()
    for pc in toPCs:
        filteredTo = filteredTo | exchanges.filter(to_currency = pc)
    exchanges = filteredTo & filteredFrom

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
    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()
    exchanges = Exchange.objects.filter(status="Open")
    exchanges = filterExchanges(request, exchanges)
    displayPerPage = 30
    totalPages = math.ceil(len(exchanges) / displayPerPage)

    if page <= 0 or page > totalPages:
        context = {'totalPages': 0, 'canPrevious': False, 'canNext': False, 
               'currentPage': 0, 'pages': [], 'profile': profile, 'platforms': platforms, 
               "emptyTableMessage": "There are no opened Exchange Requests", "exchanges": [],
               "messages": [MESSAGES[get_user_language(request).name]["INVALID_PAGE"]]}
        return render(request, 'exchange/exchanges_list.html', context)

    startPagination = max(page - 2, 1)
    endPagination = min(totalPages, startPagination + 4) + 1
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
        return HttpResponseRedirect('/exchanges/history/{}/page=1/'.format(request.user.username))
    user = get_user_model().objects.filter(username=username).first()
    if user is None:
        return HttpResponseRedirect('/exchanges/history/{}/page=1/'.format(request.user.username))
    profile = Profile.objects.filter(user=user).first()
    platforms = Platform.objects.all()
    exchanges = Exchange.objects.filter(creator=profile) | Exchange.objects.filter(exchanged_by=profile)

    exchanges = filterExchanges(request, exchanges)

    displayPerPage = 30
    totalPages = math.ceil(len(exchanges) / displayPerPage)

    if page <= 0 or page > totalPages:
        context = {'totalPages': 0, 'canPrevious': False, 'canNext': False, 
               'currentPage': 0, 'pages': [], 'profile': profile, 'platforms': platforms, 
               "emptyTableMessage": "You have no exchanges in your history", "exchanges": []}
        return render(request, 'exchange/exchanges_history.html', context)

    startPagination = max(page - 2, 1)
    endPagination = min(totalPages, startPagination + 4) + 1
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
    if exchange is None:
        return HttpResponseRedirect(reverse('index'))

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
    if ticket is None:
        return HttpResponseRedirect(reverse('index'))
    messages = SupportTicketMessage.objects.filter(ticket=ticket)
    context = {'profile': profile, 'platforms': platforms, 'ticket': ticket, 'messages': messages}
    return render(request, 'support/ticket.html', context)

    
@login_required
@require_http_methods(["GET", "POST"])
def createTicket(request):
    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()
    categories = SupportCategory.objects.all().order_by('order')
    context = {'profile': profile, 'platforms': platforms, 'categories': categories, 'messages': []}

    if request.method == "POST":
        context["messages"] = get_support_create_errors(request)
        if len(context["messages"]) > 0:
            return render(request, 'support/create_ticket.html', context)

        title = request.POST["title"]
        category = SupportCategory.objects.filter(order=request.POST["category"]).first()
        if category is None:
            return HttpResponseRedirect(reverse('index'))
        message = request.POST["message"]
        creator = profile
        ticket = SupportTicket.objects.create(creator=creator, title=title, category=category)
        SupportTicketMessage.objects.create(ticket=ticket, sender=creator, message=message)
        return redirect('/support/ticket/' + str(ticket.ticketId) + "/")

    return render(request, 'support/create_ticket.html', context)
