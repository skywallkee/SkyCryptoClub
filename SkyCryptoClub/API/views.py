from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import permissions
from SkyCryptoClub.API.serializers import UserSerializer, ProfileSerializer, UserRoleSerializer, RoleSerializer, \
                                          ProfileBanSerializer, PlatformSerializer, PlatformCurrencySerializer, \
                                          CurrencySerializer, WalletSerializer, AccountSerializer, ExchangeTaxPeerSerializer, \
                                          PasswordTokenSerializer, ExchangeSerializer, TwoFactorLoginSerializer, ExchangeStatusSerializer, \
                                          FAQCategorySerializer, QuestionSerializer, StatisticsSerializer, PublicityBannersSerializer
from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from .models import User, Profile, Role, UserRole, ProfileBan, Platform, PlatformCurrency, Currency, Wallet, \
                    Account, PasswordToken, Exchange, ExchangeStatus, TwoFactorLogin, ExchangeTaxPeer, \
                    FAQCategory, Question, Statistics, FoundDeposit, PublicityBanners
import json


from ..GLOBAL import EMAIL as gEMAIL, PASSWORD as gPASSWORD, STAKE_TOKEN, TOTP
from ..APIS import send_mail
from ..MESSAGES import TFA_HTML, TFA_TEXT, TFA_SUBJECT
from ..METHODS import get_json_data
from multiprocessing import Process
import time
from decimal import *

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


class StatisticsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows profile statistics to be viewed or edited.
    """
    queryset = Statistics.objects.all()
    serializer_class = StatisticsSerializer
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


def user_login(request):
    if request.method != 'POST':
        return HttpResponse(400)
    data = get_json_data(json.loads(request.body), ["username", "password"])
    if len(data) != 2:
        return HttpResponse(400)
    username, password = data
    user = authenticate(username=username, password=password)
    if not user or not user.is_active:
        return HttpResponse(400)
    TFA = TwoFactorLogin.objects.filter(user=user, valid_until__gt=timezone.now()).first()
    if not TFA:
        TFA = TwoFactorLogin.objects.create(user=user)
    key = TFA.key
    send_TFA_mail = Process(target=send_mail, args=(user.email, TFA_SUBJECT, TFA_TEXT.format(key), TFA_HTML.format(key)))
    send_TFA_mail.start()
    return HttpResponse(200)

def check_tfa(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data["username"]
        password = data["password"]
        tfa = data["2FA"]
        user = authenticate(username=username, password=password)
        tfalist = TwoFactorLogin.objects.filter(user=user)
        for twfa in tfalist:
            if twfa.key == tfa and timezone.now() < twfa.valid_until:
                return HttpResponse(200)
    else:
        return HttpResponse(400)
    print("Someone tried to login and failed.")
    print("They used username: {} and password: {} with 2FA: {}".format(username,password, tfa))
    return HttpResponse(400)

def get_balances(request):
    if not request.user.is_authenticated:
        return HttpResponse(400)
    if request.method == 'POST':
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
    else:
        return HttpResponse(400)

def get_platform_currencies(request):
    if not request.user.is_authenticated:
        return HttpResponse(400)
    if request.method == 'POST':
        data = json.loads(request.body)
        platform = data["platform"]
        currencies = []
        for currency in PlatformCurrency.objects.filter(platform=platform):
            currencies.append([currency.currency.name, currency.currency.largeName])
        return JsonResponse(currencies, safe=False)
    else:
        return HttpResponse(400)

def get_platform_accounts(request):
    if not request.user.is_authenticated:
        return HttpResponse(400)
    if request.method == 'POST':
        data = json.loads(request.body)
        platform = Platform.objects.filter(id=data["platform"]).first()
        profile = Profile.objects.filter(user=request.user).first()
        accountsList = Account.objects.filter(profile=profile, platform=platform, active=True)
        accounts = []
        for account in accountsList:
            accounts.append(account.username)
        return JsonResponse(accounts, safe=False)
    else:
        return HttpResponse(400)

def get_available_balance(request):
    if not request.user.is_authenticated:
        return HttpResponse(400)
    if request.method == 'POST':
        data = json.loads(request.body)
        platform = Platform.objects.filter(id=data["platform"]).first()
        currency = Currency.objects.filter(name=data["currency"]).first()
        profile = Profile.objects.filter(user=request.user).first()
        store = PlatformCurrency.objects.filter(platform=platform, currency=currency).first()
        wallet = Wallet.objects.filter(profile=profile, store=store).first()
        return JsonResponse({"amount": "{0:.8f}".format(wallet.amount)}, safe=False)
    else:
        return HttpResponse(400)

def reload_stake(accounts, platform, profile):
    import requests
    url = "https://api.stake.com/graphql"
    searching = True
    offset = 0
    limit = 50
    found = []
    while searching:
        payload = "{\"query\":\"{\\n user {\\n tipList(limit: " + str(limit) + ", offset: " + str(offset) + ") {\\n id\\n currency\\n amount\\n sendBy {\\n name\\n }\\n }\\n}\\n}\"}"
        headers = {
        'Content-Type': 'application/json',
        'x-access-token': STAKE_TOKEN
        }
        response = requests.request("POST", url, headers=headers, data = payload)
        tipList = response.json()['data']['user']['tipList']
        if len(tipList) < 1:
            searching = False
        for tip in tipList:
            account = accounts.filter(username=tip['sendBy']['name'])
            if len(account) > 0:
                account = account.first()
                if len(FoundDeposit.objects.filter(tipId=tip['id'], platform=platform)) > 0:
                    searching = False
                else:
                    currency = Currency.objects.filter(name=tip['currency']).first()
                    store = PlatformCurrency.objects.filter(currency=currency, platform=platform).first()
                    amount = tip['amount']
                    wallet = Wallet.objects.filter(profile=profile, store=store).first()
                    print(wallet.amount)
                    wallet.amount += Decimal(amount)
                    print(wallet.amount)
                    wallet.save()
                    FoundDeposit.objects.create(tipId=tip['id'], profile=profile, platform=platform, account=account)
        offset += limit

def reload_balance(request):
    if not request.user.is_authenticated:
        return HttpResponse(400)
    if request.method == 'POST':
        data = json.loads(request.body)
        profile = Profile.objects.filter(user=request.user).first()
        platform = Platform.objects.filter(id=data["platform"]).first()
        accounts = Account.objects.filter(platform=platform, profile=profile, active=True)
        if platform.name == "Stake":
            reload_stake(accounts, platform ,profile)
    return HttpResponse(200)

def find_user_id_stake(username):
    if not request.user.is_authenticated:
        return HttpResponse(400)
    import requests
    url = "https://api.stake.com/graphql"
    payload = "{\"query\":\"query {\\n user(name: \\\"" + username + "\\\") {\\n id\\n}\\n}\"}"
    headers = {
    'Content-Type': 'application/json',
    'x-access-token': STAKE_TOKEN,
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data = payload)
    user = response.json()["data"]["user"]
    if "id" in user:
        return user["id"]
    else:
        return None

def do_withdraw_stake(platform, currency, amount, username):
    if not request.user.is_authenticated:
        return HttpResponse(400)
    import requests
    url = "https://api.stake.com/graphql"
    userId = find_user_id_stake(username)
    if userId is None:
        return None
    else:
        payload = "{\"query\":\"mutation SendTipMutation {\\nsendTip(userId: \\\"" + userId + "\\\", amount: " + str(amount) + ", currency: " + currency.name + ", isPublic: true, chatId: \\\"f0326994-ee9e-411c-8439-b4997c187b95\\\", tfaToken: \"" + TOTP.now() + "\") {\\nid\\namount\\ncurrency}\\n}\"}"
        headers = {
        'Content-Type': 'application/json',
        'x-access-token': STAKE_TOKEN,
        'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data = payload)
        result = response.json()
        if "errors" in response:
            return None
    return 200

def do_withdraw(platform, currency, amount, username):
    if not request.user.is_authenticated:
        return HttpResponse(400)
    if platform.name == "Stake":
        response = do_withdraw_stake(platform, currency, amount, username)
        return response
    return 400

def withdraw(request):
    if not request.user.is_authenticated:
        return HttpResponse(400)
    if request.method == 'POST':
        data = json.loads(request.body)
        platform = Platform.objects.filter(id=data["platform"]).first()
        currency = Currency.objects.filter(name=data["currency"]).first()
        amount = Decimal(data["amount"])
        username = data["account"]

        profile = Profile.objects.filter(user=request.user).first()
        store = PlatformCurrency.objects.filter(platform=platform, currency=currency).first()
        wallet = Wallet.objects.filter(profile=profile, store=store).first()
        if wallet.amount > amount:
            if do_withdraw(platform, currency, amount, username) == 200:
                wallet.amount -= amount
                wallet.save()
                return HttpResponse(200)
    return HttpResponse(400)

def closeExchange(request):
    if not request.user.is_authenticated:
        return HttpResponse(400)
    if request.method == 'POST':
        data = json.loads(request.body)
        exchange = Exchange.objects.filter(eid=data["eid"]).first()
        if exchange.creator.user == request.user:
            closed = ExchangeStatus.objects.filter(status="Closed").first()
            exchange.status = closed
            exchange.save()
            return HttpResponse(200)
    return HttpResponse(400)

def openExchange(request):
    if not request.user.is_authenticated:
        return HttpResponse(400)
    if request.method == 'POST':
        data = json.loads(request.body)
        exchange = Exchange.objects.filter(eid=data["eid"]).first()
        if exchange.creator.user == request.user:
            open = ExchangeStatus.objects.filter(status="Open").first()
            exchange.status = open
            exchange.save()
            return HttpResponse(200)
    return HttpResponse(400)

def payExchange(request):
    if not request.user.is_authenticated:
        return HttpResponse(403)
    if request.method == 'POST':
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
        # Add to creator the promised balance
        wallet = Wallet.objects.filter(profile=exchange.creator, store=exchange.to_currency).first()
        wallet.amount += exchange.creator_amount
        wallet.save()
        # Set exchanger to the exchange and close it
        exchanger = Profile.objects.filter(user=request.user).first()
        completed = ExchangeStatus.objects.filter(status="Completed").first()
        exchange.exchanged_by = exchanger
        exchange.status = completed
        exchange.save()
        return HttpResponse(200)
    return HttpResponse(403)