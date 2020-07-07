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
from ..APIS import send_mail
from ..MESSAGES import MESSAGES
from ..METHODS import get_json_data, generate_password
from ..API.views import get_user_language, user_login_form, user_register_form, contact_send_mail, \
                        settings_update_avatar, settings_update_credentials, change_privacy, \
                        remove_linked_account, find_user_stake, confirm_stake_account, confirm_linked_account, \
                        filterExchanges
from ..API.validator import get_support_create_errors
import string
import random
import os
from decimal import *
import math
from django.core.paginator import Paginator
from .filters import ExchangeFilter

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


@require_http_methods(["GET", "POST"])
def user_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))

    if request.method == "POST":
        return user_login_form(request)

    template    = loader.get_template('registration/login.html')
    return HttpResponse(template.render({}, request))


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
    text = MESSAGES[get_user_language(request).name]["RECOVERY_MAIL"]["MESSAGE"].format(user.email, user.username, password)
    html = MESSAGES[get_user_language(request).name]["RECOVERY_MAIL"]["HTML"].format(user.email, user.username, password)
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


@require_http_methods(["GET", "POST"])
def contact(request):
    context = {}

    if request.method == "POST":
        context =  contact_send_mail(request)

    template    = loader.get_template('WEB/contact.html')
    return HttpResponse(template.render(context, request))

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


@login_required
@require_http_methods(["GET"])
def exchanges(request, page):
    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()

    exchanges = Exchange.objects.filter(status="Open").order_by('eid')
    exchangeFilter = ExchangeFilter(request.GET, exchanges)
    exchanges = exchangeFilter.qs

    displayPerPage = 30
    paginator = Paginator(exchanges, displayPerPage)

    totalPages = paginator.num_pages

    if page <= 0 or page > totalPages:
        context = {'totalPages': 0, 'canPrevious': False, 'canNext': False, 
                'currentPage': 1, 'pages': [], 'profile': profile, 'platforms': platforms, 
                "emptyTableMessage": "There are no opened Exchange Requests", "exchanges": [],
                "messages": [MESSAGES[get_user_language(request).name]["INVALID_PAGE"]],
                "exchangeFilter": exchangeFilter}
        return render(request, 'exchange/exchanges_list.html', context)

    startPagination = max(page - 2, 1)
    endPagination = min(totalPages, startPagination + 4) + 1
    pages = [i for i in range(startPagination, endPagination)]
    canNext = paginator.page(page).has_next()
    canPrevious = paginator.page(page).has_previous()
    exchanges = paginator.page(page).object_list

    context = {'totalPages': totalPages, 'canPrevious': canPrevious, 'canNext': canNext, 
               'currentPage': page, 'pages': pages, 'profile': profile, 'platforms': platforms, 
               "emptyTableMessage": "There are no opened Exchange Requests", "exchanges": exchanges,
                "exchangeFilter": exchangeFilter}
    return render(request, 'exchange/exchanges_list.html', context)


def exchanges_history(request, page):
    return HttpResponseRedirect('/exchanges/history/{}/page={}/'.format(request.user.username, page))
    

@login_required
@require_http_methods(["GET", "POST"])
def exchanges_history_user(request, username, page):
    if not request.user.username == username:
        return HttpResponseRedirect('/exchanges/history/{}/page=1/'.format(request.user.username))
    user = get_user_model().objects.filter(username=username).first()
    if user is None:
        return HttpResponseRedirect('/exchanges/history/{}/page=1/'.format(request.user.username))
    profile = Profile.objects.filter(user=user).first()
    platforms = Platform.objects.all()
    
    exchanges = Exchange.objects.filter(status="Open").order_by('eid')
    exchangeFilter = ExchangeFilter(request.GET, exchanges)
    exchanges = exchangeFilter.qs

    displayPerPage = 30
    paginator = Paginator(exchanges, displayPerPage)

    totalPages = paginator.num_pages

    if page <= 0 or page > totalPages:
        context = {'totalPages': 0, 'canPrevious': False, 'canNext': False, 
               'currentPage': 1, 'pages': [], 'profile': profile, 'platforms': platforms, 
               "emptyTableMessage": "You have no exchanges in your history", "exchanges": [],
                "messages": [MESSAGES[get_user_language(request).name]["INVALID_PAGE"]],
                "exchangeFilter": exchangeFilter}
        return render(request, 'exchange/exchanges_history.html', context)

    startPagination = max(page - 2, 1)
    endPagination = min(totalPages, startPagination + 4) + 1
    pages = [i for i in range(startPagination, endPagination)]
    canNext = paginator.page(page).has_next()
    canPrevious = paginator.page(page).has_previous()
    exchanges = paginator.page(page).object_list

    context = {'totalPages': totalPages, 'canPrevious': canPrevious, 'canNext': canNext, 
               'currentPage': page, 'pages': pages, 'profile': profile, 'platforms': platforms, 
               "emptyTableMessage": "You have no exchanges in your history", "exchanges": exchanges,
                "exchangeFilter": exchangeFilter}
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
    context = {'profile': profile, 'platforms': platforms, 'ticket': ticket, 'ticket_messages': messages}
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