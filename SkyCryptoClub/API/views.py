from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import permissions
from SkyCryptoClub.API.serializers import UserSerializer, ProfileSerializer, UserRoleSerializer, RoleSerializer, \
                                          ProfileBanSerializer, PlatformSerializer, PlatformCurrencySerializer, \
                                          CurrencySerializer, WalletSerializer, AccountSerializer, ExchangeTaxPeerSerializer, \
                                          PasswordTokenSerializer, ExchangeSerializer, TwoFactorLoginSerializer, ExchangeStatusSerializer, \
                                          FAQCategorySerializer, QuestionSerializer, PublicityBannersSerializer, InvitationSerializer
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from .models import User, Profile, Role, UserRole, ProfileBan, Platform, PlatformCurrency, Currency, Wallet, \
                    Account, PasswordToken, Exchange, ExchangeStatus, TwoFactorLogin, ExchangeTaxPeer, \
                    FAQCategory, Question, FoundDeposit, PublicityBanners, \
                    SupportTicket, SupportTicketMessage, SupportCategory, Languages, Invitation, \
                    Withdrawal
import json


from ..GLOBAL import EMAIL as gEMAIL, PASSWORD as gPASSWORD, STAKE_TOKEN, TOTP
from ..APIS import send_mail, get_user_language, api_request
from ..MESSAGES import MESSAGES
from ..METHODS import get_json_data, generate_password
from multiprocessing import Process
import time
from decimal import *
import os
from .validator import valid_login, valid_tfa, valid_register, get_settings_update_errors, \
                       get_settings_update_avatar_errors, get_support_create_errors
from ..decorators import not_exchange_banned, not_platform_banned

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = get_user_model().objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class PasswordTokenViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = PasswordToken.objects.all()
    serializer_class = PasswordTokenSerializer
    permission_classes = [permissions.IsAdminUser]


class TwoFactorLoginViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = TwoFactorLogin.objects.all()
    serializer_class = TwoFactorLoginSerializer
    permission_classes = [permissions.IsAdminUser]


class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows profiles to be viewed or edited.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAdminUser]


class InvitationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows profiles to be viewed or edited.
    """
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAdminUser]


class UserRoleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows user roles to be viewed or edited.
    """
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [permissions.IsAdminUser]


class RoleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows roles to be viewed or edited.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAdminUser]


class ProfileBanViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows bans to be viewed or edited.
    """
    queryset = ProfileBan.objects.all()
    serializer_class = ProfileBanSerializer
    permission_classes = [permissions.IsAdminUser]


class PlatformViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows platforms to be viewed or edited.
    """
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer
    permission_classes = [permissions.IsAdminUser]


class PlatformCurrencyViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows platform currencies to be viewed or edited.
    """
    queryset = PlatformCurrency.objects.all()
    serializer_class = PlatformCurrencySerializer
    permission_classes = [permissions.IsAdminUser]


class CurrencyViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows currency to be viewed or edited.
    """
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [permissions.IsAdminUser]


class WalletViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows currency to be viewed or edited.
    """
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAdminUser]


class AccountViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows currency to be viewed or edited.
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAdminUser]


class ExchangeStatusViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows exchanges to be viewed or edited.
    """
    queryset = ExchangeStatus.objects.all()
    serializer_class = ExchangeStatusSerializer
    permission_classes = [permissions.IsAdminUser]


class ExchangeTaxPeerViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows exchanges to be viewed or edited.
    """
    queryset = ExchangeTaxPeer.objects.all()
    serializer_class = ExchangeTaxPeerSerializer
    permission_classes = [permissions.IsAdminUser]


class ExchangeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows exchanges to be viewed or edited.
    """
    queryset = Exchange.objects.all()
    serializer_class = ExchangeSerializer
    permission_classes = [permissions.IsAdminUser]


class FAQCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows FAQ categories to be viewed or edited.
    """
    queryset = FAQCategory.objects.all()
    serializer_class = FAQCategorySerializer
    permission_classes = [permissions.IsAdminUser]


class QuestionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows questions to be viewed or edited.
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAdminUser]


class PublicityBannersViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows banners to be viewed or edited.
    """
    queryset = PublicityBanners.objects.all()
    serializer_class = PublicityBannersSerializer
    permission_classes = [permissions.IsAdminUser]


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def valid_captcha(request):
    if not 'g-recaptcha-response' in request.POST and not 'g-recaptcha-response' in json.loads(request.body):
        return False
    if 'g-recaptcha-response' in request.POST:
        captcha = request.POST.get('g-recaptcha-response')
    else:
        captcha = json.loads(request.body)['g-recaptcha-response']
    import requests
    content = requests.post(
        'https://www.google.com/recaptcha/api/siteverify',
        data={
            'secret': os.environ['GOOGLE_RECAPTCHA_SECRET_KEY'],
            'response': captcha,
        }
    ).content
    content = json.loads( content )
    return 'success' in content and content['success']


@require_http_methods(["POST"])
def has_tfa(request):
    data = get_json_data(json.loads(request.body), ["username"])
    if len(data) != 1:
        return JsonResponse({"response": 400}, safe=False)
    username, = data
    user = get_user_model().objects.filter(username=username).first()
    if not user:
        return JsonResponse({"response": 400}, safe=False)
    profile = Profile.objects.filter(user=user).first()
    return JsonResponse({"response": 200, "tfa": profile.twofactor})

@require_http_methods(["POST"])
def user_login(request):
    data = get_json_data(json.loads(request.body), ["username", "password"])
    if len(data) != 2:
        return HttpResponse(400)
    username, password = data
    user = authenticate(username=username, password=password)
    if not user or not user.is_active:
        return HttpResponse(400)
    profile = Profile.objects.filter(user=user).first()
    if profile.twofactor:
        TFA = TwoFactorLogin.objects.filter(user=user, valid_until__gt=timezone.now()).first()
        if not TFA:
            TFA = TwoFactorLogin.objects.create(user=user)
        key = TFA.key
        send_TFA_mail = Process(target=send_mail, args=(user.email, MESSAGES[get_user_language(request).name]["TFA_MAIL"]["SUBJECT"], MESSAGES[get_user_language(request).name]["TFA_MAIL"]["MESSAGE"].format(key), MESSAGES[get_user_language(request).name]["TFA_MAIL"]["HTML"].format(key)))
        send_TFA_mail.start()
    return HttpResponse(200)


def user_login_form(request):
    data    = get_json_data(request.POST, ["username", "password", "2FA"])
    if len(data) != 3:
        return HttpResponseRedirect(reverse('login'))

    username, password, tfa = data

    if not valid_login(username, password):
        return HttpResponseRedirect(reverse('login'))
    
    user = authenticate(username=username, password=password)

    if user is None:
        return HttpResponseRedirect(reverse('login'))

    profile = Profile.objects.filter(user=user).first()
    if not valid_tfa(user, tfa) and profile.twofactor == True:
        return HttpResponseRedirect(reverse('login'))

    login(request, user)
    try:
        TwoFactorLogin.objects.filter(user=user).delete()
    except:
        pass

    return HttpResponseRedirect(reverse('index'))


@require_http_methods(["POST"])
def check_tfa(request):
    data = json.loads(request.body)
    username = data["username"]
    password = data["password"]
    tfa = data["2FA"]
    user = authenticate(username=username, password=password)
    if not user:
        return HttpResponse(400)
    tfalist = TwoFactorLogin.objects.filter(user=user)
    for twfa in tfalist:
        if twfa.key == tfa and timezone.now() < twfa.valid_until:
            return HttpResponse(200)
    print("Someone tried to login and failed.")
    print("They used username: {} and password: {} with 2FA: {}".format(username,password, tfa))
    return HttpResponse(400)


def user_register_form(request):
    data    = get_json_data(request.POST, ['username', 'email'])
    if len(data) != 2:
        return {"success": False, "messages": [MESSAGES[get_user_language(request)]["REGISTER"]["FAIL"]]}

    username, email = data

    if not valid_register(username, email):
        return {"success": False, "messages": [MESSAGES[get_user_language(request).name]["REGISTER"]["FAIL"]]}

    password = generate_password()
    User.objects.create_user(username, email, password)

    subject             = MESSAGES[get_user_language(request).name]["REGISTER_MAIL"]["SUBJECT"]
    text                = MESSAGES[get_user_language(request).name]["REGISTER_MAIL"]["MESSAGE"].format(email, username, password)
    html                = MESSAGES[get_user_language(request).name]["REGISTER_MAIL"]["HTML"].format(email, username, password)
    send_mail_process   = Process(target=send_mail, args=(email, subject, text, html))
    send_mail_process.start()
    return {"success": True, "messages": [MESSAGES[get_user_language(request).name]["REGISTER"]["SUCCESS"]]}


def contact_send_mail(request):
    data    = get_json_data(request.POST, ['email', 'subject', 'message'])
    if len(data) != 3:
        return {"messages": [MESSAGES[get_user_language(request).name]["CONTACT_US"]["FAIL"]["INCOMPLETE"]]}

    email, subject, message = data

    if email == "" or subject == "" or message == "":
        return {"messages": [MESSAGES[get_user_language(request).name]["CONTACT_US"]["FAIL"]["INCOMPLETE"]]}

    message = email + ": " + message

    send_mail_process   = Process(target=send_mail, args=(os.environ["CONTACT_MAIL"], "CONTACT FORM: " + subject, message, message))
    send_mail_process.start()
    send_mail_process   = Process(target=send_mail, args=(email, subject, message, message))
    send_mail_process.start()
    return {"messages": [MESSAGES[get_user_language(request).name]["CONTACT_US"]["SUCCESS"]]}


@login_required
@require_http_methods(["POST"])
def get_balances(request):
    data = json.loads(request.body)
    platform = data["platform"]
    profile = Profile.objects.filter(user=request.user).first()
    userWallets = Wallet.objects.filter(profile=profile)
    wallets = []
    currencies = PlatformCurrency.objects.filter(platform=platform)      
    for currency in currencies:
        wallet = userWallets.filter(store=currency).first()
        wallets.append([wallet.store.currency.name, "{0:.8f}".format(wallet.amount)])
    wallets = sorted(wallets, key=lambda currency: currency[1], reverse=True)
    return JsonResponse(wallets, safe=False)

@login_required
@require_http_methods(["POST"])
def get_platform_currencies(request):
    data = json.loads(request.body)
    platform = data["platform"]
    currencies = []
    for currency in PlatformCurrency.objects.filter(platform=platform):
        currencies.append([currency.currency.name, currency.currency.largeName])
    return JsonResponse(currencies, safe=False)

@login_required
@require_http_methods(["POST"])
def get_platform_accounts(request):
    data = json.loads(request.body)
    platform = Platform.objects.filter(id=data["platform"]).first()
    profile = Profile.objects.filter(user=request.user).first()
    accountsList = Account.objects.filter(profile=profile, platform=platform, active=True)
    accounts = []
    for account in accountsList:
        accounts.append(account.username)
    return JsonResponse(accounts, safe=False)

@login_required
@require_http_methods(["POST"])
def get_available_balance(request):
    data = json.loads(request.body)
    platform = Platform.objects.filter(id=data["platform"]).first()
    currency = Currency.objects.filter(name=data["currency"]).first()
    profile = Profile.objects.filter(user=request.user).first()
    store = PlatformCurrency.objects.filter(platform=platform, currency=currency).first()
    wallet = Wallet.objects.filter(profile=profile, store=store).first()
    return JsonResponse({"amount": "{0:.8f}".format(wallet.amount)}, safe=False)

def reload_stake(accounts, platform, profile):
    import requests
    url = "https://api.stake.com/graphql"
    searching = True
    offset = 0
    limit = 50
    found = []
    while searching:
        payload = "{\"query\":\"{ user { tipList(limit: " + str(limit) + ", offset: " + str(offset) + ") { id currency amount sendBy { name } }}}\"}"
        headers = {
        'Content-Type': 'application/json',
        'x-access-token': STAKE_TOKEN
        }
        response = requests.request("POST", url, headers=headers, data = payload)
        tipList = response.json()['data']['user']['tipList']
        print(response.json())
        if len(tipList) < 1:
            searching = False
        for tip in tipList:
            account = accounts.filter(username=tip['sendBy']['name']).first()
            if account:
                if FoundDeposit.objects.filter(tipId=tip['id'], platform=platform).first():
                    searching = False
                else:
                    currency = Currency.objects.filter(name=tip['currency']).first()
                    store = PlatformCurrency.objects.filter(currency=currency, platform=platform).first()
                    amount = tip['amount']
                    wallet = Wallet.objects.filter(profile=profile, store=store).first()
                    wallet.amount += Decimal(amount)
                    wallet.save()
                    FoundDeposit.objects.create(tipId=tip['id'], profile=profile, platform=platform, account=account)
        offset += limit - 1

@login_required
@require_http_methods(["POST"])
def reload_balance(request):
    data = json.loads(request.body)
    profile = Profile.objects.filter(user=request.user).first()
    platform = Platform.objects.filter(id=data["platform"]).first()
    accounts = Account.objects.filter(platform=platform, profile=profile, active=True)
    if platform.name == "Stake":
        reload_stake(accounts, platform ,profile)
    return HttpResponse(200)

def find_user_id_stake(username):
    import requests
    url = "https://api.stake.com/graphql"
    payload = "{\"query\":\"query { user(name: \\\"" + username + "\\\") { id }}\"}"
    headers = {
    'Content-Type': 'application/json',
    'x-access-token': STAKE_TOKEN,
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data = payload)
    result = response.json()
    print(result)
    if "errors" in result:
        return None
    user = result["data"]["user"]
    if "id" in user:
        return user["id"]
    else:
        return None

def do_withdraw_stake(platform, currency, amount, username):
    import requests
    url = "https://api.stake.com/graphql"
    userId = find_user_id_stake(username)
    if userId is None:
        return None
    else:
        payload = "{\"query\":\"mutation SendTipMutation { sendTip(userId: \\\"" + userId + "\\\", amount: " + str(amount) + ", currency: " + currency.name + ", isPublic: true, chatId: \\\"f0326994-ee9e-411c-8439-b4997c187b95\\\", tfaToken: \\\"" + TOTP.now() + "\\\") {id amount currency}}\"}"
        headers = {
        'Content-Type': 'application/json',
        'x-access-token': STAKE_TOKEN,
        'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data = payload)
        result = response.json()
        print(result)
        if "errors" in result:
            return None
    return result["data"]["sendTip"]

def do_withdraw(platform, currency, amount, username):
    if platform.name == "Stake":
        response = do_withdraw_stake(platform, currency, amount, username)
        return response
    return None

def add_vault_stake(currency, amount):
    import requests
    url = "https://api.stake.com/graphql"
    payload = "{\"query\":\"mutation CreateVaultDepositMutation { createVaultDeposit(amount: " + str(amount) + ", currency: " + currency + ") { id } }\"}"
    headers = {
    'Content-Type': 'application/json',
    'x-access-token': STAKE_TOKEN,
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data = payload)
    result = response.json()
    if "data" not in result or not result["data"] or "errors" in result:
        return None
    return 200

def add_vault(platform, currency, amount):
    if platform.name == "Stake":
        response = add_vault_stake(currency, amount)
        return response
    return 400

@login_required
@require_http_methods(["POST"])
def withdraw(request):
    data = json.loads(request.body)
    platform = Platform.objects.filter(id=data["platform"]).first()
    currency = Currency.objects.filter(name=data["currency"]).first()
    amount = Decimal(data["amount"])
    username = data["account"]

    profile = Profile.objects.filter(user=request.user).first()
    account = Account.objects.filter(profile=profile, platform=platform, username=username).first()
    if not account or not platform or not currency:
        return HttpResponse(400)
    store = PlatformCurrency.objects.filter(platform=platform, currency=currency).first()
    if not store:
        return HttpResponse(400)
    wallet = Wallet.objects.filter(profile=profile, store=store).first()
    if wallet.amount > amount:
        result = do_withdraw(platform, currency, amount, username)
        if not result:
            return HttpResponse(400)
        Withdrawal.objects.create(tipId=result["id"], profile=profile, account=account)
        wallet.amount -= amount
        wallet.save()
        return HttpResponse(200)
    return HttpResponse(400)

@login_required
@require_http_methods(["POST"])
def closeExchange(request):
    data = json.loads(request.body)
    exchange = Exchange.objects.filter(eid=data["eid"]).first()
    if exchange.creator.user == request.user:
        closed = ExchangeStatus.objects.filter(status="Closed").first()
        exchange.status = closed
        exchange.save()

        creatorWallet = Wallet.objects.filter(profile=exchange.creator, store=exchange.from_currency).first()
        creatorWallet.amount += exchange.from_amount
        creatorWallet.save()
        return HttpResponse(200)
    return HttpResponse(400)

@login_required
@require_http_methods(["POST"])
def openExchange(request):
    data = json.loads(request.body)
    exchange = Exchange.objects.filter(eid=data["eid"]).first()
    if exchange.creator.user == request.user and exchange.status.status == "Pending":
        open = ExchangeStatus.objects.filter(status="Open").first()
        exchange.status = open
        exchange.save()
        return HttpResponse(200)
    return HttpResponse(400)

@login_required
@require_http_methods(["POST"])
def payExchange(request):
    prices = {
        "eth": 39.11,
        "ltc": 217.52,
        "doge": 3093838.04,
        "bch": 41.04,
        "xrp": 47002.64,
        "trx": 534954,
        "eos": 3644.21,
        "btc": 1,
    }
    data = json.loads(request.body)
    exchange = Exchange.objects.filter(eid=data["eid"]).first()
    if exchange.status.status != "Open":
        return HttpResponse(403)
    profile = Profile.objects.filter(user=request.user).first()
    wallet = Wallet.objects.filter(profile=profile, store=exchange.to_currency).first()
    # Check if exchanger has enough balance and extract it
    if wallet.amount < exchange.to_amount:
        return HttpResponse(400)
    wallet.amount -= exchange.to_amount
    wallet.save()
    # Add to exchanger the promised balance
    wallet = Wallet.objects.filter(profile=profile, store=exchange.from_currency).first()
    wallet.amount += exchange.exchanger_amount
    wallet.save()
    # Add profit from exchanger to vault
    remaining_from_exchanger = exchange.from_amount - exchange.exchanger_amount
    to_vault = Decimal(0.9) * remaining_from_exchanger
    to_vault = to_vault.quantize(Decimal('.00000001'), rounding="ROUND_DOWN")
    to_xp_creator = Decimal(0.1) * remaining_from_exchanger
    to_xp_creator = to_xp_creator.quantize(Decimal('.00000001'), rounding="ROUND_DOWN")
    add_vault(exchange.from_currency.platform, exchange.from_currency.currency.name, to_vault)
    # Add to creator the promised balance
    wallet = Wallet.objects.filter(profile=exchange.creator, store=exchange.to_currency).first()
    wallet.amount += exchange.creator_amount
    wallet.save()
    # Add profit from creator to vault
    remaining_from_creator = exchange.to_amount - exchange.creator_amount
    to_vault = Decimal(0.9) * remaining_from_creator
    to_vault = to_vault.quantize(Decimal('.00000001'), rounding="ROUND_DOWN")
    to_xp_exchanger = Decimal(0.1) * remaining_from_creator
    to_xp_exchanger = to_xp_exchanger.quantize(Decimal('.00000001'), rounding="ROUND_DOWN")
    add_vault(exchange.to_currency.platform, exchange.to_currency.currency.name, remaining_from_creator)
    # Add xp to parties
    xp_creator = to_xp_creator * Decimal(100000000) / Decimal(prices[exchange.from_currency.currency.name])
    exchange.creator.xp = exchange.creator.xp + xp_creator
    exchange.creator.save()
    xp_exchanger = to_xp_exchanger * Decimal(100000000) / Decimal(prices[exchange.to_currency.currency.name])
    profile = Profile.objects.filter(user=request.user).first()
    profile.xp = profile.xp + xp_exchanger
    profile.save()
    # Set exchanger to the exchange and close it
    exchanger = Profile.objects.filter(user=request.user).first()
    completed = ExchangeStatus.objects.filter(status="Completed").first()
    exchange.exchanged_by = exchanger
    exchange.status = completed
    exchange.save()
    return HttpResponse(200)

@login_required
@require_http_methods(["POST"])
def exchangeAmount(request):
    data = json.loads(request.body)
    try:
        givenAmount = Decimal(data["givenAmount"])
    except:
        givenAmount = Decimal(0)

    try:
        receivedAmount = Decimal(data["receivedAmount"])
    except:
        receivedAmount = Decimal(0)

    currency = Currency.objects.filter(name=data["currency"]).first()

    if not currency:
        return HttpResponse(400)
    if data["backwards"]:
        toCompare = receivedAmount
    else:
        toCompare = givenAmount
    tax = Decimal(1) - ExchangeTaxPeer.objects.filter(currency=currency).filter().filter(minAmount__lte=toCompare).filter(maxAmount__gte=toCompare).first().percentage / Decimal(100)

    if data["backwards"]:
        givenAmount = receivedAmount / tax
    else:
        receivedAmount = givenAmount * tax

    return JsonResponse({"givenAmount": "{0:.8f}".format(givenAmount),
                         "receivedAmount": "{0:.8f}".format(receivedAmount),}, 
                         safe=False)


@login_required
@require_http_methods(["POST"])
def closeTicket(request):
    data = json.loads(request.body)
    if "tid" not in data:
        return HttpResponse(400)
    profile = Profile.objects.filter(user=request.user).first()
    userRoles = UserRole.objects.filter(profile=profile)
    canClose = False
    for uRole in userRoles:
        if uRole.role.closeTickets:
            canClose = True
    ticket = SupportTicket.objects.filter(ticketId=data["tid"]).first()
    if not ticket or ticket.closed:
        return HttpResponse(400)
    if not canClose and ticket.creator != profile:
        return HttpResponse(400)
    closingMessage = SupportTicketMessage.objects.create(ticket=ticket, sender=profile, message="Closed the ticket!")
    ticket.closed = True
    ticket.save()
    return HttpResponse(200)


@login_required
@require_http_methods(["POST"])
def openTicket(request):
    data = json.loads(request.body)
    if "tid" not in data:
        return HttpResponse(400)
    profile = Profile.objects.filter(user=request.user).first()
    userRoles = UserRole.objects.filter(profile=profile)
    canOpen = False
    for uRole in userRoles:
        if uRole.role.closeTickets:
            canOpen = True
    ticket = SupportTicket.objects.filter(ticketId=data["tid"]).first()
    if not ticket or not ticket.closed:
        return HttpResponse(400)
    if not canOpen and ticket.creator != profile:
        return HttpResponse(400)
    openingMessage = SupportTicketMessage.objects.create(ticket=ticket, sender=profile, message="Opened the ticket!")
    ticket.closed = False
    ticket.save()
    return HttpResponse(200)


@login_required
@require_http_methods(["POST"])
def replyTicket(request):
    data = json.loads(request.body)
    if "tid" not in data and "message" not in data:
        return HttpResponse(400)
    if data["tid"] == "" or type(data["tid"]) != int or data["message"] == "":
        return HttpResponse(400)
    profile = Profile.objects.filter(user=request.user).first()
    userRoles = UserRole.objects.filter(profile=profile)
    canReply = False
    for uRole in userRoles:
        if uRole.role.respondTickets:
            canReply = True
    ticket = SupportTicket.objects.filter(ticketId=data["tid"]).first()
    if not ticket or ticket.closed:
        return HttpResponse(400)
    if not canReply and ticket.creator != profile:
        return HttpResponse(400)
    ticket.last_replied = profile
    ticket.save()
    newMessage = SupportTicketMessage.objects.create(ticket=ticket, sender=profile, message=data["message"])
    return HttpResponse(200)

def settings_update_avatar(request, context, profile):
    if 'newAvatar' not in request.FILES:
        return context["messages"].append(MESSAGES[get_user_language(request).name]["AVATAR"]["FAIL"]["NO_IMAGE"])
    avatar = request.FILES['newAvatar']
    context["messages"] = get_settings_update_avatar_errors(request, avatar)

    if len(context["messages"]) == 0:
        profile.avatar = avatar
        profile.save()
        context["messages"].append(MESSAGES[get_user_language(request).name]["AVATAR"]["SUCCESS"])
    return context


def settings_update_credentials(request, context):
    data = get_json_data(request.POST, ('email', 'password', 'newpass', 'newpassconfirm', 'twofactor'))
    if len(data) != 5:
        context["messages"] = [MESSAGES[get_user_language(request).name]["INVALID_INPUT"]]
        return context
    email, password, newpass, newpassconfirm, twofactor = data

    context["messages"] = get_settings_update_errors(request, email, password, newpass, newpassconfirm, twofactor)
    
    if len(context["messages"]) == 0:
        twofactor = twofactor == "True"
        profile = Profile.objects.filter(user=request.user).first()
        if twofactor != profile.twofactor:
            profile.twofactor = twofactor
            profile.save()
            context["messages"].append(MESSAGES[get_user_language(request).name]["TWO_FACTOR"]["SUCCESS"])
        if email != request.user.email:
            request.user.email = email
            request.user.save()
            context["messages"].append(MESSAGES[get_user_language(request).name]["EMAIL"]["SUCCESS"])
        if len(newpass) > 0:
            request.user.set_password(newpass)
            request.user.save()
            context["messages"].append(MESSAGES[get_user_language(request).name]["PASSWORD"]["SUCCESS"])
    return context


def change_privacy(request, profile):
    data = get_json_data(request.POST, ("publicStats", "publicLevel", "publicXP", "publicName"))
    publicStats, publicLevel, publicXP, publicName = data
    profile.publicStats = publicStats == "true"
    profile.publicLevel = publicLevel == "true"
    profile.publicXP = publicXP == "true"
    profile.publicName = publicName == "true"
    profile.save()
    return [MESSAGES[get_user_language(request).name]["PRIVACY"]["SUCCESS"]]


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
    payload = "{\"query\":\"query { user { name }}\"}"
    headers = {'x-access-token': api,}
    data = api_request(url, payload, headers, "POST")
    if "data" not in data:
        return None
    if "user" not in data["data"]:
        return None
    if "name" not in data["data"]["user"]:
        return None
    return data["data"]["user"]["name"]


def confirm_stake_account(request, username, key, platform):
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
    if username == "" or platform == "" or key == "":
        context["messages"] = [MESSAGES[get_user_language(request).name]["ACCOUNT_LINK"]["FAIL"]["INVALID_API"]]
        return context
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


def isSupport(profile):
    for role in UserRole.objects.filter(profile=profile):
        if role.role.viewTickets == True:
            return True
    return False

def canBan(profile):
    canBanExchange = False
    canBanWithdraw = False
    canBanTemporary = False
    canBanPermanent = False
    for role in UserRole.objects.filter(profile=profile):
        if role.role.banUser:
            canBanTemporary = True
        if role.role.banExchange:
            canBanExchange = True
        if role.role.banWithdraw:
            canBanWithdraw = True
        if role.role.permanentBan:
            canBanPermanent = True
    return canBanTemporary or canBanExchange or canBanWithdraw or canBanPermanent

@login_required
@require_http_methods(["POST"])
def deleteFAQ(request):
    data = json.loads(request.body)
    question = Question.objects.filter(id=data["id"]).first()
    profile = Profile.objects.filter(user=request.user).first()
    if not profile:
        return HttpResponse(400)
    canDelete = False
    for role in UserRole.objects.filter(profile=profile):
        if role.role.removeFAQ:
            canDelete = True
    if canDelete:
        question.delete()
        return HttpResponse(200)
    return HttpResponse(400)

@login_required
@require_http_methods(["POST"])
def unban(request):
    data = json.loads(request.body)
    ban = ProfileBan.objects.filter(id=data["id"]).first()
    profile = Profile.objects.filter(user=request.user).first()
    if not profile:
        return HttpResponse(400)
    canUnban = False
    for role in UserRole.objects.filter(profile=profile):
        if role.role.unban:
            canUnban = True
    if canUnban:
        ban.banDue = timezone.now()
        ban.save()
        return HttpResponse(200)
    return HttpResponse(400)


def get_usd_price(coin):
    coin_ids = {
        "btc": "bitcoin",
        "eth": "ethereum",
        "ltc": "litecoin",
        "doge": "dogecoin",
        "bch": "bitcoin-cash",
        "xrp": "ripple",
        "trx": "tron",
        "eos": "eos",
    }
    url = "https://api.coingecko.com/api/v3/coins/{}?localization=false&tickers=false&community_data=false&developer_data=false&sparkline=false".format(coin_ids[coin])

    import requests
    content = requests.get(url).content
    content = json.loads(content)
    return float(content["market_data"]["current_price"]["usd"])


def exchangeRate(request):
    data = get_json_data(json.loads(request.body), ("fromCurrency", "fromAmount", "toCurrency", "toAmount"))
    if len(data) != 4:
        return HttpResponse(0)
    fromCurrency, fromAmount, toCurrency, toAmount = data

    fromUSDAmount = get_usd_price(fromCurrency)
    fromAmount = float(fromAmount) * fromUSDAmount

    toUSDAmount = get_usd_price(toCurrency)

    getcontext().prec = 8
    rate = Decimal(fromAmount) / Decimal(toUSDAmount)
    return HttpResponse(rate.quantize(Decimal('.00000001'), rounding="ROUND_DOWN"))