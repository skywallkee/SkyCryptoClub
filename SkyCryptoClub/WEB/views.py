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
                         SupportTicket, SupportTicketMessage, SupportCategory, Invitation, FoundDeposit, \
                         Withdrawal, ProfileBan
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
                        filterExchanges, isSupport, canBan
from ..API.validator import get_support_create_errors
import string
import random
import os
from decimal import *
import math
from django.core.paginator import Paginator
from .filters import ExchangeFilter, DepositFilter, WithdrawFilter
from django.conf import settings as DjangoSettings
from ratelimit.decorators import ratelimit
from ..decorators import not_exchange_banned, not_platform_banned
from djqscsv import render_to_csv_response

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

@ratelimit(block=True, key='ip', rate='20/m')
def index(request):
    template    = loader.get_template('WEB/index.html')
    isPlatformBanned = False
    if request.user.is_authenticated:
        profile = Profile.objects.filter(user=request.user).first()
        bans = ProfileBan.objects.filter(profile=profile, totalBan=True, banDue__gte=timezone.now())
        if len(bans) > 0 and not request.user.is_staff:
            isPlatformBanned = True
    context     = {"banners": get_banners(), "isPlatformBanned": isPlatformBanned}
    return HttpResponse(template.render(context, request))


@ratelimit(block=True, key='ip', rate='20/m')
@require_http_methods(["GET", "POST"])
def user_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))

    if request.method == "POST":
        return user_login_form(request)

    template    = loader.get_template('registration/login.html')
    return HttpResponse(template.render({}, request))


@ratelimit(block=True, key='ip', rate='20/m')
@require_http_methods(["GET", "POST"])
def user_register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))

    template    = loader.get_template('registration/register.html')
    context     = {}
    invitation = None

    if "SCC_Invitation_Code" in request.COOKIES:
        invitation = Invitation.objects.filter(code=request.COOKIES["SCC_Invitation_Code"]).first()
    
    if (not invitation or (invitation.registrations >= invitation.limit and invitation.limit != -1)) and DjangoSettings.CLOSED_REGISTRATION:
        return HttpResponseRedirect(reverse('index'))
    
    invitation.clicks += 1
    invitation.save()

    if request.method == 'POST':
        context = user_register_form(request)
        if context["success"]:
            invitation.registrations += 1
            invitation.save()

    return HttpResponse(template.render(context, request))


@ratelimit(block=True, key='ip', rate='20/m')
@require_http_methods(["GET"])
def user_register_invitation(request, invitation):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    response = HttpResponseRedirect(reverse('register'))
    response.set_cookie(key="SCC_Invitation_Code", value=invitation, max_age=None)
    return response


@ratelimit(block=True, key='ip', rate='20/m')
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


@ratelimit(block=True, key='ip', rate='20/m')
@require_http_methods(["GET"])
def faq(request):
    categories = FAQCategory.objects.all()
    answers = Question.objects.filter(accepted=True)
    context = {"categories": categories, "answers": answers}
    return render(request, 'WEB/faq.html', context)


@ratelimit(block=True, key='ip', rate='20/m')
@require_http_methods(["GET"])
def terms(request):
    context = {}
    return render(request, 'WEB/terms.html', context)


@ratelimit(block=True, key='ip', rate='20/m')
@require_http_methods(["GET", "POST"])
def contact(request):
    context = {}

    if request.method == "POST":
        context =  contact_send_mail(request)

    template    = loader.get_template('WEB/contact.html')
    return HttpResponse(template.render(context, request))

@not_platform_banned
@login_required
@ratelimit(block=True, key='user_or_ip', rate='15/m')
@require_http_methods(["GET"])
def dashboard(request):
    return HttpResponseRedirect('/dashboard/{}'.format(request.user.username))

@not_platform_banned
@login_required
@ratelimit(block=True, key='user_or_ip', rate='15/m')
@require_http_methods(["GET"])
def dashboard_user(request, username):
    user = get_user_model().objects.filter(username=username).first()

    if user is None:
        return HttpResponseRedirect(reverse('dashboard'))

    is_owner = user.username == request.user.username

    profile = Profile.objects.filter(user=user).first()
    currentProfile = Profile.objects.filter(user=request.user).first()
    statistics = {}
    statistics["totalExchangesStarted"] = len(Exchange.objects.filter(creator=profile))
    statistics["totalExchanges"] = len(Exchange.objects.filter(exchanged_by=profile))
    
    title = ""
    if profile.publicLevel or is_owner or isSupport(currentProfile):
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

    currentUserProfile = Profile.objects.filter(user=request.user).first()
    
    isWithdrawBanned = False
    bans = ProfileBan.objects.filter(profile=currentProfile, withdrawBan=True, banDue__gte=timezone.now())
    if len(bans) > 0 or not request.user.is_staff:
        isWithdrawBanned = True
    context = {'profile': profile, 'statistics': statistics,
               'title': title, 'platforms': platforms,
               'owner': is_owner, 'name_color': name_color,
               'is_support': isSupport(currentProfile),
               'canBan': canBan(currentUserProfile),
               'isWithdrawBanned': isWithdrawBanned}
    return render(request, 'dashboard/profile.html', context)

@not_platform_banned
@login_required
@ratelimit(block=True, key='user_or_ip', rate='15/m')
@require_http_methods(["GET", "POST"])
def settings(request):
    context = {}
    if request.method == "POST":
        if "updateAvatar" in request.POST:
            context = settings_update_avatar(request, context, profile)
        else:
            context = settings_update_credentials(request, context)

    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()
    
    isWithdrawBanned = False
    bans = ProfileBan.objects.filter(profile=profile, withdrawBan=True, banDue__gte=timezone.now())
    if len(bans) > 0 or not request.user.is_staff:
        isWithdrawBanned = True
    context['profile'] = profile
    context['platforms'] = platforms
    context['is_support'] = isSupport(profile)
    context['canBan'] = canBan(profile)
    context['isWithdrawBanned'] = isWithdrawBanned
    return render(request, 'settings/settings.html', context)

@not_platform_banned
@login_required
@ratelimit(block=True, key='user_or_ip', rate='15/m')
@require_http_methods(["GET", "POST"])
def privacy(request):
    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()
    
    isWithdrawBanned = False
    bans = ProfileBan.objects.filter(profile=profile, withdrawBan=True, banDue__gte=timezone.now())
    if len(bans) > 0 or not request.user.is_staff:
        isWithdrawBanned = True
    context = {'profile': profile,
               'platforms': platforms,
               'is_support': isSupport(profile),
               'canBan': canBan(profile),
               'isWithdrawBanned': isWithdrawBanned}

    if request.method == "POST":
        context["messages"] = change_privacy(request, profile)

    return render(request, 'settings/privacy.html', context)

@not_platform_banned
@login_required
@ratelimit(block=True, key='user_or_ip', rate='15/m')
@require_http_methods(["GET", "POST"])
def linked(request):
    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()
    
    isWithdrawBanned = False
    bans = ProfileBan.objects.filter(profile=profile, withdrawBan=True, banDue__gte=timezone.now())
    if len(bans) > 0 or not request.user.is_staff:
        isWithdrawBanned = True
    context = {'profile': profile, 'platforms': platforms,
               'is_support': isSupport(profile),
               'canBan': canBan(profile),
               'isWithdrawBanned': isWithdrawBanned}
    if request.method == "POST":
        if 'removeAccount' in request.POST:
            context = remove_linked_account(request, context)
        if 'addAccount' in request.POST:
            context = confirm_linked_account(request, context)
    linked = Account.objects.filter(profile=profile)
    context["linked"] = linked
    return render(request, 'settings/linked.html', context)

@not_platform_banned
@not_exchange_banned
@login_required
@ratelimit(block=True, key='user_or_ip', rate='10/m')
@require_http_methods(["GET", "POST"])
def requestExchange(request):
    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()
    
    isWithdrawBanned = False
    bans = ProfileBan.objects.filter(profile=profile, withdrawBan=True, banDue__gte=timezone.now())
    if len(bans) > 0 or not request.user.is_staff:
        isWithdrawBanned = True
    context = {'profile': profile, 'platforms': platforms, "emptyTableMessage": MESSAGES[get_user_language(request).name]["EMPTY_EXCHANGE_TABLE"], 
               "exchanges": exchanges, 'is_support': isSupport(profile), 'canBan': canBan(profile), 'isWithdrawBanned': isWithdrawBanned}
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

@not_platform_banned
@not_exchange_banned
@login_required
@ratelimit(block=True, key='user_or_ip', rate='15/m')
@require_http_methods(["GET"])
def exchanges(request, page):
    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()
    
    isWithdrawBanned = False
    bans = ProfileBan.objects.filter(profile=profile, withdrawBan=True, banDue__gte=timezone.now())
    if len(bans) > 0 or not request.user.is_staff:
        isWithdrawBanned = True

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
                "exchangeFilter": exchangeFilter, 'is_support': isSupport(profile), 'canBan': canBan(profile),
                'isWithdrawBanned': isWithdrawBanned}
        return render(request, 'exchange/exchanges_list.html', context)

    startPagination = max(page - 2, 1)
    endPagination = min(totalPages, startPagination + 4) + 1
    pages = [i for i in range(startPagination, endPagination)]
    canNext = paginator.page(page).has_next()
    canPrevious = paginator.page(page).has_previous()
    exchanges = paginator.page(page).object_list

    canCloseExchanges = False
    isModerator = False
    for role in UserRole.objects.filter(profile=profile):
        if role.role.moderationPanel:
            isModerator = True
        if role.role.closeExchange:
            canCloseExchanges = True
    
    context = {'totalPages': totalPages, 'canPrevious': canPrevious, 'canNext': canNext, 
               'currentPage': page, 'pages': pages, 'profile': profile, 'platforms': platforms, 
               "emptyTableMessage": "There are no opened Exchange Requests", "exchanges": exchanges,
                "exchangeFilter": exchangeFilter, 'is_support': isSupport(profile), 'canBan': canBan(profile),
                "isModerator": isModerator, "canCloseExchanges": canCloseExchanges,
                'isWithdrawBanned': isWithdrawBanned}
    return render(request, 'exchange/exchanges_list.html', context)

@not_platform_banned
@ratelimit(block=True, key='ip', rate='15/m')
def exchanges_history(request, page):
    return HttpResponseRedirect('/transactions/exchange/{}/page={}/'.format(request.user.username, page))
    
@not_platform_banned
@login_required
@ratelimit(block=True, key='user_or_ip', rate='15/m')
@require_http_methods(["GET", "POST"])
def exchanges_history_user(request, username, page):
    currentProfile = Profile.objects.filter(user=request.user).first()
    if not request.user.username == username and not isSupport(currentProfile):
        return HttpResponseRedirect('/transactions/exchange/{}/page=1/'.format(request.user.username))
    user = get_user_model().objects.filter(username=username).first()
    if user is None:
        return HttpResponseRedirect('/transactions/exchange/{}/page=1/'.format(request.user.username))
    profile = Profile.objects.filter(user=user).first()
    platforms = Platform.objects.all()
    
    isWithdrawBanned = False
    bans = ProfileBan.objects.filter(profile=currentProfile, withdrawBan=True, banDue__gte=timezone.now())
    if len(bans) > 0 or not request.user.is_staff:
        isWithdrawBanned = True
    
    exchanges = (Exchange.objects.filter(creator=profile) | Exchange.objects.filter(exchanged_by=profile)).order_by('eid')
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
                "exchangeFilter": exchangeFilter, 'is_support': isSupport(currentProfile), 'canBan': canBan(currentProfile),
                'isWithdrawBanned': isWithdrawBanned}
        return render(request, 'transactions/exchanges_history.html', context)

    startPagination = max(page - 2, 1)
    endPagination = min(totalPages, startPagination + 4) + 1
    pages = [i for i in range(startPagination, endPagination)]
    canNext = paginator.page(page).has_next()
    canPrevious = paginator.page(page).has_previous()
    exchanges = paginator.page(page).object_list

    context = {'totalPages': totalPages, 'canPrevious': canPrevious, 'canNext': canNext, 
               'currentPage': page, 'pages': pages, 'profile': profile, 'platforms': platforms, 
               "emptyTableMessage": "You have no exchanges in your history", "exchanges": exchanges,
                "exchangeFilter": exchangeFilter, 'is_support': isSupport(currentProfile), 'canBan': canBan(currentProfile),
                'isWithdrawBanned': isWithdrawBanned}
    return render(request, 'transactions/exchanges_history.html', context)

@not_platform_banned
@ratelimit(block=True, key='ip', rate='15/m')
def deposits_history(request, page):
    return HttpResponseRedirect('/transactions/deposit/{}/page={}/'.format(request.user.username, page))
    
@not_platform_banned
@login_required
@ratelimit(block=True, key='user_or_ip', rate='15/m')
@require_http_methods(["GET", "POST"])
def deposits_history_user(request, username, page):
    currentProfile = Profile.objects.filter(user=request.user).first()
    if not request.user.username == username and not isSupport(currentProfile):
        print(1)
        return HttpResponseRedirect('/transactions/deposit/{}/page=1/'.format(request.user.username))
    user = get_user_model().objects.filter(username=username).first()
    if user is None:
        return HttpResponseRedirect('/transactions/deposit/{}/page=1/'.format(request.user.username))
    profile = Profile.objects.filter(user=user).first()
    platforms = Platform.objects.all()
    
    isWithdrawBanned = False
    bans = ProfileBan.objects.filter(profile=profile, withdrawBan=True, banDue__gte=timezone.now())
    if len(bans) > 0 or not request.user.is_staff:
        isWithdrawBanned = True

    deposits = FoundDeposit.objects.filter(profile=profile).order_by('tipId')
    
    depositFilter = DepositFilter(request.GET, deposits, profile=profile)
    deposits = depositFilter.qs

    displayPerPage = 30
    paginator = Paginator(deposits, displayPerPage)

    totalPages = paginator.num_pages

    if page <= 0 or page > totalPages:
        context = {'totalPages': 0, 'canPrevious': False, 'canNext': False, 
               'currentPage': 1, 'pages': [], 'profile': profile, 'platforms': platforms, 
               "emptyTableMessage": "You have no deposits in your history", "deposits": [],
                "messages": [MESSAGES[get_user_language(request).name]["INVALID_PAGE"]],
                "depositFilter": depositFilter, 'is_support': isSupport(currentProfile), 'canBan': canBan(currentProfile),
                'isWithdrawBanned': isWithdrawBanned}
        return render(request, 'transactions/deposits_history.html', context)

    startPagination = max(page - 2, 1)
    endPagination = min(totalPages, startPagination + 4) + 1
    pages = [i for i in range(startPagination, endPagination)]
    canNext = paginator.page(page).has_next()
    canPrevious = paginator.page(page).has_previous()
    deposits = paginator.page(page).object_list

    context = {'totalPages': totalPages, 'canPrevious': canPrevious, 'canNext': canNext, 
               'currentPage': page, 'pages': pages, 'profile': profile, 'platforms': platforms, 
               "emptyTableMessage": "You have no deposits in your history", "deposits": deposits,
                "depositFilter": depositFilter, 'is_support': isSupport(currentProfile), 'canBan': canBan(currentProfile),
                'isWithdrawBanned': isWithdrawBanned}
    return render(request, 'transactions/deposits_history.html', context)

@not_platform_banned
@ratelimit(block=True, key='ip', rate='15/m')
def withdraws_history(request, page):
    return HttpResponseRedirect('/transactions/withdraw/{}/page={}/'.format(request.user.username, page))
    
@not_platform_banned
@login_required
@ratelimit(block=True, key='user_or_ip', rate='15/m')
@require_http_methods(["GET", "POST"])
def withdraws_history_user(request, username, page):
    currentProfile = Profile.objects.filter(user=request.user).first()
    if not request.user.username == username and not isSupport(currentProfile):
        return HttpResponseRedirect('/transactions/withdraw/{}/page=1/'.format(request.user.username))
    user = get_user_model().objects.filter(username=username).first()
    if user is None:
        return HttpResponseRedirect('/transactions/withdraw/{}/page=1/'.format(request.user.username))
    profile = Profile.objects.filter(user=user).first()
    platforms = Platform.objects.all()
    
    isWithdrawBanned = False
    bans = ProfileBan.objects.filter(profile=currentProfile, withdrawBan=True, banDue__gte=timezone.now())
    if len(bans) > 0 or not request.user.is_staff:
        isWithdrawBanned = True

    withdraws = Withdrawal.objects.filter(profile=profile).order_by('tipId')
    
    withdrawFilter = WithdrawFilter(request.GET, withdraws, profile=profile)
    withdraws = withdrawFilter.qs

    displayPerPage = 30
    paginator = Paginator(withdraws, displayPerPage)

    totalPages = paginator.num_pages

    if page <= 0 or page > totalPages:
        context = {'totalPages': 0, 'canPrevious': False, 'canNext': False, 
               'currentPage': 1, 'pages': [], 'profile': profile, 'platforms': platforms, 
               "emptyTableMessage": "You have no withdrawals in your history", "withdraws": [],
                "messages": [MESSAGES[get_user_language(request).name]["INVALID_PAGE"]],
                "withdrawFilter": withdrawFilter, 'is_support': isSupport(currentProfile), 'canBan': canBan(currentProfile),
                'isWithdrawBanned': isWithdrawBanned}
        return render(request, 'transactions/withdraws_history.html', context)

    startPagination = max(page - 2, 1)
    endPagination = min(totalPages, startPagination + 4) + 1
    pages = [i for i in range(startPagination, endPagination)]
    canNext = paginator.page(page).has_next()
    canPrevious = paginator.page(page).has_previous()
    withdraws = paginator.page(page).object_list

    context = {'totalPages': totalPages, 'canPrevious': canPrevious, 'canNext': canNext, 
               'currentPage': page, 'pages': pages, 'profile': profile, 'platforms': platforms, 
               "emptyTableMessage": "You have no withdrawals in your history", "withdraws": withdraws,
                "withdrawFilter": withdrawFilter, 'is_support': isSupport(currentProfile), 'canBan': canBan(currentProfile),
                'isWithdrawBanned': isWithdrawBanned}
    return render(request, 'transactions/withdraws_history.html', context)

@not_platform_banned
@login_required
@ratelimit(block=True, key='user_or_ip', rate='5/m')
@require_http_methods(["GET"])
def exchanges_csv(request):
    profile = Profile.objects.filter(user=request.user).first()
    exchanges = Exchange.objects.filter(creator=profile) | Exchange.objects.filter(exchanged_by=profile)
    exchanges = exchanges.values('eid', 'creator__user__username', 'from_currency__currency__name', 'from_currency__platform__name', 'from_amount', 
                                 'to_currency__currency__name', 'to_currency__platform__name', 'to_amount', 'exchanged_by__user__username',
                                  'creator_amount', 'exchanger_amount', 'ratio', 'status', 'taxCreator__percentage', 'taxExchanger__percentage', 'created_at')
    return render_to_csv_response(exchanges)

@not_platform_banned
@login_required
@ratelimit(block=True, key='user_or_ip', rate='5/m')
@require_http_methods(["GET"])
def deposits_csv(request):
    profile = Profile.objects.filter(user=request.user).first()
    depositList = FoundDeposit.objects.filter(profile=profile)
    depositList = depositList.values('tipId', 'profile__user__username', 'account__username')
    return render_to_csv_response(depositList)

@not_platform_banned
@login_required
@ratelimit(block=True, key='user_or_ip', rate='5/m')
@require_http_methods(["GET"])
def withdraws_csv(request):
    profile = Profile.objects.filter(user=request.user).first()
    withdrawList = Withdrawal.objects.filter(profile=profile)
    withdrawList = withdrawList.values('tipId', 'profile__user__username', 'account__username')
    return render_to_csv_response(withdrawList)

@not_platform_banned
@not_exchange_banned
@login_required
@ratelimit(block=True, key='user_or_ip', rate='15/m')
@require_http_methods(["GET"])
def exchange_page(request, exchange_id):
    exchange = Exchange.objects.filter(eid=exchange_id).first()
    if exchange is None:
        return HttpResponseRedirect(reverse('index'))

    profile = Profile.objects.filter(user=request.user).first()
    
    isWithdrawBanned = False
    bans = ProfileBan.objects.filter(profile=profile, withdrawBan=True, banDue__gte=timezone.now())
    if len(bans) > 0 or not request.user.is_staff:
        isWithdrawBanned = True
    platforms = Platform.objects.all()
    context = {'profile': profile, 'platforms': platforms, "exchange": exchange, 
                'is_support': isSupport(profile), 'canBan': canBan(profile),
                'isWithdrawBanned': isWithdrawBanned}
    return render(request, 'exchange/exchange.html', context)

@not_platform_banned
@login_required
@ratelimit(block=True, key='user_or_ip', rate='15/m')
@require_http_methods(["GET"])
def support(request):
    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()
    tickets = SupportTicket.objects.filter(creator=profile).order_by('-created_at')
    if isSupport(profile):
        tickets = tickets | SupportTicket.objects.filter(closed=False)
    
    isWithdrawBanned = False
    bans = ProfileBan.objects.filter(profile=profile, withdrawBan=True, banDue__gte=timezone.now())
    if len(bans) > 0 or not request.user.is_staff:
        isWithdrawBanned = True
    platforms = Platform.objects.all()
    context = {'profile': profile, 'platforms': platforms, 'tickets': tickets, 
                'is_support': isSupport(profile), 'canBan': canBan(profile),
                'isWithdrawBanned': isWithdrawBanned}
    return render(request, 'support/contact_support.html', context)

@not_platform_banned
@login_required
@ratelimit(block=True, key='user_or_ip', rate='15/m')
@require_http_methods(["GET"])
def ticket(request, tid):
    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()
    ticket = SupportTicket.objects.filter(ticketId=tid).first()
    if ticket is None:
        return HttpResponseRedirect(reverse('index'))
    messages = SupportTicketMessage.objects.filter(ticket=ticket)
    
    isWithdrawBanned = False
    bans = ProfileBan.objects.filter(profile=profile, withdrawBan=True, banDue__gte=timezone.now())
    if len(bans) > 0 or not request.user.is_staff:
        isWithdrawBanned = True
    context = {'profile': profile, 'platforms': platforms, 'ticket': ticket, 
            'ticket_messages': messages, 'is_support': isSupport(profile), 'canBan': canBan(profile),
            'isWithdrawBanned': isWithdrawBanned}
    return render(request, 'support/ticket.html', context)

@not_platform_banned
@login_required
@ratelimit(block=True, key='user_or_ip', rate='10/m')
@require_http_methods(["GET", "POST"])
def createTicket(request):
    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()
    categories = SupportCategory.objects.all().order_by('order')
    
    isWithdrawBanned = False
    bans = ProfileBan.objects.filter(profile=profile, withdrawBan=True, banDue__gte=timezone.now())
    if len(bans) > 0 or not request.user.is_staff:
        isWithdrawBanned = True
    context = {'profile': profile, 'platforms': platforms, 'categories': categories, 
                'messages': [], 'is_support': isSupport(profile), 'canBan': canBan(profile),
                'isWithdrawBanned': isWithdrawBanned}

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

@not_platform_banned
@login_required
@ratelimit(block=True, key='user_or_ip', rate='30/m')
@require_http_methods(["GET", "POST"])
def faqPanel(request):
    profile = Profile.objects.filter(user=request.user).first()
    if not isSupport(profile):
        return HttpResponseRedirect(reverse('index'))
    platforms = Platform.objects.all()
    categories = FAQCategory.objects.all()
    questions = Question.objects.all()
    canDelete = False
    canEdit = False
    canAdd = False
    for role in UserRole.objects.filter(profile=profile):
        if role.role.removeFAQ:
            canDelete = True
        if role.role.editFAQ:
            canEdit = True
        if role.role.addFAQ:
            canAdd = True
    
    isWithdrawBanned = False
    bans = ProfileBan.objects.filter(profile=profile, withdrawBan=True, banDue__gte=timezone.now())
    if len(bans) > 0 or not request.user.is_staff:
        isWithdrawBanned = True
    context = {'profile': profile, 'platforms': platforms, 'categories': categories, 
               'questions': questions, 'messages': [], 'is_support': isSupport(profile),
               'canDelete': canDelete, 'canEdit': canEdit, 'canAdd': canAdd, 'canBan': canBan(profile),
               'isWithdrawBanned': isWithdrawBanned}
    return render(request, 'support/faq_panel.html', context)

@not_platform_banned
@login_required
@ratelimit(block=True, key='user_or_ip', rate='30/m')
@require_http_methods(["GET", "POST"])
def faqEdit(request, question_id):
    profile = Profile.objects.filter(user=request.user).first()
    if not isSupport(profile):
        return HttpResponseRedirect(reverse('index'))
    platforms = Platform.objects.all()
    categories = FAQCategory.objects.all()
    question = Question.objects.filter(id=question_id).first()
    if not question:
         return redirect('/support/faq/')
    
    isWithdrawBanned = False
    bans = ProfileBan.objects.filter(profile=profile, withdrawBan=True, banDue__gte=timezone.now())
    if len(bans) > 0 or not request.user.is_staff:
        isWithdrawBanned = True
    context = {'profile': profile, 'platforms': platforms, 'categories': categories, 
               'messages': [], 'is_support': isSupport(profile),
               'question': question, 'canBan': canBan(profile), 'isWithdrawBanned': isWithdrawBanned}

    if request.method == "POST":
        data = get_json_data(request.POST, ['category', 'question', 'answer'])
        if len(data) != 3:
            return render(request, 'support/edit_faq.html', context)
        newCategory, newQuestion, newAnswer = data
        newCategory = FAQCategory.objects.filter(id=newCategory).first()
        if not newCategory or newQuestion == "" or newAnswer == "":
            return render(request, 'support/edit_faq.html', context)
        question.category = newCategory
        question.question = newQuestion
        question.answer = newAnswer
        question.save()
        return redirect('/support/faq/')

    return render(request, 'support/edit_faq.html', context)

@not_platform_banned
@login_required
@ratelimit(block=True, key='user_or_ip', rate='30/m')
@require_http_methods(["GET", "POST"])
def faqNew(request):
    profile = Profile.objects.filter(user=request.user).first()
    if not isSupport(profile):
        return HttpResponseRedirect(reverse('index'))
    platforms = Platform.objects.all()
    categories = FAQCategory.objects.all()
    
    isWithdrawBanned = False
    bans = ProfileBan.objects.filter(profile=profile, withdrawBan=True, banDue__gte=timezone.now())
    if len(bans) > 0 or not request.user.is_staff:
        isWithdrawBanned = True
    context = {'profile': profile, 'platforms': platforms, 'categories': categories, 
               'messages': [], 'is_support': isSupport(profile), 'canBan': canBan(profile),
               'isWithdrawBanned': isWithdrawBanned}

    if request.method == "POST":
        data = get_json_data(request.POST, ['category', 'question', 'answer'])
        if len(data) != 3:
            return render(request, 'support/add_faq.html', context)
        category, question, answer = data
        category = FAQCategory.objects.filter(id=category).first()
        if not category or question == "" or answer == "":
            return render(request, 'support/add_faq.html', context)
        Question.objects.create(category=category, question=question, answer=answer)
        return redirect('/support/faq/')

    return render(request, 'support/add_faq.html', context)

@not_platform_banned
@login_required
@ratelimit(block=True, key='user_or_ip', rate='30/m')
@require_http_methods(["GET", "POST"])
def bans(request):
    profile = Profile.objects.filter(user=request.user).first()
    if not canBan(profile):
        return HttpResponseRedirect(reverse('index'))
    platforms = Platform.objects.all()
    bans = ProfileBan.objects.filter(banDue__gt=timezone.now())
    canUnban = False
    for role in UserRole.objects.filter(profile=profile):
        if role.role.unban:
            canUnban = True
    
    isWithdrawBanned = False
    bans = ProfileBan.objects.filter(profile=profile, withdrawBan=True, banDue__gte=timezone.now())
    if len(bans) > 0 or not request.user.is_staff:
        isWithdrawBanned = True

    context = {'profile': profile, 'platforms': platforms, 
               'messages': [], 'is_support': isSupport(profile),
               'bans': bans, 'canBan': canBan(profile),
               'canUnban': canUnban, 'isWithdrawBanned': isWithdrawBanned}
    return render(request, 'moderator/ban_panel.html', context)

@not_platform_banned
@login_required
@ratelimit(block=True, key='user_or_ip', rate='30/m')
@require_http_methods(["GET", "POST"])
def banUser(request, username):
    userBanned = get_user_model().objects.filter(username=username).first()
    if not userBanned:
        return HttpResponseRedirect(reverse('bans'))
    banned = Profile.objects.filter(user=userBanned).first()
    if not userBanned:
        return HttpResponseRedirect(reverse('bans'))
    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()
    categories = FAQCategory.objects.all()

    canBanExchange = False
    canBanWithdraw = False
    canBanTemporary = False
    canBanPermanent = False
    for role in UserRole.objects.filter(profile=currentUserProfile):
        if role.role.banUser:
            canBanTemporary = True
        if role.role.banExchange:
            canBanExchange = True
        if role.role.banWithdraw:
            canBanWithdraw = True
        if role.role.permanentBan:
            canBanPermanent = True
    
    currentUserProfile = Profile.objects.filter(user=request.user).first()
    if not canBan(currentUserProfile):
        return HttpResponseRedirect(reverse('index'))
    
    if request.method == "POST":
        data = get_json_data(request.POST, ['exchangeBan', 'withdrawBan', 'platformBan', 'duration', 'reason'])
        exchangeBan, withdrawBan, platformBan, duration, reason = data
        exchangeBan = exchangeBan == "True"
        withdrawBan = withdrawBan == "True"
        platformBan = platformBan == "True"
        if not duration.isnumeric():
            return HttpResponseRedirect(reverse('bans'))
        duration = int(duration)
        banDue = timezone.now() + timezone.timedelta(hours=duration)
        if canBanPermanent and duration == 0:
            banDue = timezone.now() + timezone.timedelta(days=356*150)
        elif duration == 0:
            return HttpResponseRedirect(reverse('bans'))
        if reason == "":
            return HttpResponseRedirect(reverse('bans'))
        ProfileBan.objects.create(profile=banned, totalBan=platformBan, exchangeBan=exchangeBan, 
                                  withdrawBan=withdrawBan, reason=reason, bannedBy=profile, banDue=banDue)
    
    isWithdrawBanned = False
    bans = ProfileBan.objects.filter(profile=profile, withdrawBan=True, banDue__gte=timezone.now())
    if len(bans) > 0 or not request.user.is_staff:
        isWithdrawBanned = True

    context = {'profile': profile, 'platforms': platforms, 'categories': categories, 
               'messages': [], 'is_support': isSupport(profile), 'username': username,
               'canBanTemporary': canBanTemporary, 'canBanPermanent': canBanPermanent,
               'canBanWithdraw': canBanWithdraw, 'canBanExchange': canBanExchange, 'canBan': canBan(profile),
               'isWithdrawBanned': isWithdrawBanned}
    return render(request, 'moderator/ban_user.html', context)

@not_platform_banned
@login_required
@ratelimit(block=True, key='user_or_ip', rate='30/m')
@require_http_methods(["GET", "POST"])
def banEdit(request, banId):
    ban = ProfileBan.objects.filter(id=banId).first()
    if not ban:
        return HttpResponseRedirect(reverse('index'))
    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()
    categories = FAQCategory.objects.all()
    currentUserProfile = Profile.objects.filter(user=request.user).first()
    if not canBan(currentUserProfile):
        return HttpResponseRedirect(reverse('index'))

    canBanExchange = False
    canBanWithdraw = False
    canBanTemporary = False
    canBanPermanent = False
    for role in UserRole.objects.filter(profile=currentUserProfile):
        if role.role.banUser:
            canBanTemporary = True
        if role.role.banExchange:
            canBanExchange = True
        if role.role.banWithdraw:
            canBanWithdraw = True
        if role.role.permanentBan:
            canBanPermanent = True
    
    if request.method == "POST":
        data = get_json_data(request.POST, ['exchangeBan', 'withdrawBan', 'platformBan', 'duration', 'reason'])
        exchangeBan, withdrawBan, platformBan, duration, reason = data
        exchangeBan = exchangeBan == "True"
        withdrawBan = withdrawBan == "True"
        platformBan = platformBan == "True"
        if not duration.isnumeric():
            return HttpResponseRedirect(reverse('bans'))
        duration = int(duration)
        banDue = timezone.now() + timezone.timedelta(hours=duration)
        if canBanPermanent and duration == 0:
            banDue = timezone.now() + timezone.timedelta(days=356*150)
        elif duration == 0:
            return HttpResponseRedirect(reverse('bans'))
        if reason == "":
            return HttpResponseRedirect(reverse('bans'))
        ban.exchangeBan = exchangeBan
        ban.withdrawBan = withdrawBan
        ban.totalBan = platformBan
        ban.banDue = banDue
        ban.reason = reason
        ban.save()

    isWithdrawBanned = False
    bans = ProfileBan.objects.filter(profile=profile, withdrawBan=True, banDue__gte=timezone.now())
    if len(bans) > 0 or not request.user.is_staff:
        isWithdrawBanned = True

    context = {'profile': profile, 'platforms': platforms, 'categories': categories, 
               'messages': [], 'is_support': isSupport(profile),
               'canBanTemporary': canBanTemporary, 'canBanPermanent': canBanPermanent,
               'canBanWithdraw': canBanWithdraw, 'canBanExchange': canBanExchange,
               'ban': ban, 'canBan': canBan(profile), 'isWithdrawBanned': isWithdrawBanned}
    return render(request, 'moderator/edit_ban.html', context)