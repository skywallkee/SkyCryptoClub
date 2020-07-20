"""SkyCryptoClub URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from rest_framework import routers
from SkyCryptoClub.API import views as APIviews
from SkyCryptoClub.WEB import views as WEBviews
from SkyCryptoClub.ChangeLog import views as CLviews
from django.contrib.sitemaps.views import sitemap
from SkyCryptoClub.WEB.sitemaps import StaticViewSitemap
from .settings import admin_page

sitemaps = {
    'static': StaticViewSitemap
}

router = routers.DefaultRouter()
router.register(r'users', APIviews.UserViewSet)
router.register(r'passwordtokens', APIviews.PasswordTokenViewSet)
router.register(r'twofactors', APIviews.TwoFactorLoginViewSet)
router.register(r'profiles', APIviews.ProfileViewSet)
router.register(r'userroles', APIviews.UserRoleViewSet)
router.register(r'roles', APIviews.RoleViewSet)
router.register(r'profilebans', APIviews.ProfileBanViewSet)
router.register(r'platforms', APIviews.PlatformViewSet)
router.register(r'currencies', APIviews.CurrencyViewSet)
router.register(r'platformcurrencies', APIviews.PlatformCurrencyViewSet)
router.register(r'wallets', APIviews.WalletViewSet)
router.register(r'accounts', APIviews.AccountViewSet)
router.register(r'exchanges', APIviews.ExchangeViewSet)
router.register(r'faqcategories', APIviews.FAQCategoryViewSet)
router.register(r'questions', APIviews.QuestionViewSet)

handler400 = 'SkyCryptoClub.WEB.views.handler400'
handler404 = 'SkyCryptoClub.WEB.views.handler404'
handler500 = 'SkyCryptoClub.WEB.views.handler500'

urlpatterns = [
    path('', WEBviews.index, name='index'),
    path(r'robots.txt', include('robots.urls')),
    path(r'sitemap.xml', sitemap, {'sitemaps': sitemaps}),
    path(r'favicon.ico', WEBviews.favicon, name='favicon'),
    path(r'banned/', WEBviews.ip_banned_page, name='ip-banned-page'),

    # API
    path(r'endpoints/', include(router.urls)),
    path(r'api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path(r'check-login/', APIviews.user_login, name='check-login'),
    path(r'check-tfa/', APIviews.check_tfa, name='check-tfa'),
    path(r'has-tfa/', APIviews.has_tfa, name='has-tfa'),
    path(r'get-balances/', APIviews.get_balances, name='get-balances'),
    path(r'get-platform-currencies/', APIviews.get_platform_currencies, name='get-platform-currencies'),
    path(r'get-available-balance/', APIviews.get_available_balance, name='get-available-balance'),
    path(r'reload-balance/', APIviews.reload_balance, name='reload-balance'),
    path(r'withdraw/', APIviews.withdraw, name='withdraw'),
    path(r'get-platform-accounts/', APIviews.get_platform_accounts, name='get-platform-accounts'),

    # ADMIN
    path(r'admin_tools/', include('admin_tools.urls')),
    path(admin_page, admin.site.urls, name='admin-panel'),

    # USER REGISTRATION
    path(r'login/', WEBviews.user_login, name='login'),
    path(r'logout/', auth_views.LogoutView.as_view(), name='logout'),
    path(r'register/', WEBviews.user_register, name='register'),
    path(r'register/<str:invitation>/', WEBviews.user_register_invitation, name='register'),
    path(r'recover/', WEBviews.recover_password, name='recover-password'),

    # FAQ & TERMS
    path(r'faq/', WEBviews.faq, name='faq'),
    path(r'terms/', WEBviews.terms, name='terms'),
    path(r'contact/', WEBviews.contact, name='contact'),

    # DASHBOARD
    path(r'dashboard/', WEBviews.dashboard, name='dashboard'),
    path(r'dashboard/<str:username>/', WEBviews.dashboard_user, name='dashboard_user'),

    # SETTINGS
    path(r'settings/', WEBviews.settings, name='settings'),
    path(r'settings/privacy/', WEBviews.privacy, name='privacy'),
    path(r'settings/linked/', WEBviews.linked, name='linked'),

    # EXCHANGES
    path(r'exchanges/page=<int:page>/', WEBviews.exchanges, name='exchanges'),
    path(r'exchanges/create/', WEBviews.requestExchange, name='request-exchange'),
    path(r'exchanges/<int:exchange_id>/', WEBviews.exchange_page, name='exchange-page'),
    path(r'delete-exchange/', APIviews.closeExchange, name='delete-exchange'),
    path(r'open-exchange/', APIviews.openExchange, name='open-exchange'),
    path(r'pay-exchange/', APIviews.payExchange, name='pay-exchange'),
    path(r'get-exchange-amount/', APIviews.exchangeAmount, name='get-exchange-amount'),

    # TRANSACTIONS
    path(r'transactions/exchange/page=<int:page>/', WEBviews.exchanges_history, name='exchanges-history'),
    path(r'transactions/exchange/<str:username>/page=<int:page>/', WEBviews.exchanges_history_user, name='exchanges-history-user'),
    path(r'transactions/deposit/page=<int:page>/', WEBviews.deposits_history, name='deposits-history'),
    path(r'transactions/deposit/<str:username>/page=<int:page>/', WEBviews.deposits_history_user, name='deposits-history-user'),
    path(r'transactions/withdraw/page=<int:page>/', WEBviews.withdraws_history, name='withdraws-history'),
    path(r'transactions/withdraw/<str:username>/page=<int:page>/', WEBviews.withdraws_history_user, name='withdraws-history-user'),
    path(r'transactions/csv/exchange/', WEBviews.exchanges_csv, name='exchanges-csv'),
    path(r'transactions/csv/deposit/', WEBviews.deposits_csv, name='deposits-csv'),
    path(r'transactions/csv/withdraw/', WEBviews.withdraws_csv, name='withdraws-csv'),

    # SUPPORT
    path(r'support/tickets/', WEBviews.support, name='support'),
    path(r'support/ticket/create/', WEBviews.createTicket, name='create-ticket'),
    path(r'support/ticket/<int:tid>/', WEBviews.ticket, name='ticket'),
    path(r'close-ticket/', APIviews.closeTicket, name='close-ticket'),
    path(r'open-ticket/', APIviews.openTicket, name='open-ticket'),
    path(r'reply-ticket/', APIviews.replyTicket, name='reply-ticket'),

    # SUPPORT FAQ
    path(r'support/faq/', WEBviews.faqPanel, name='faq-panel'),
    path(r'support/faq/<int:question_id>/', WEBviews.faqEdit, name='faq-edit'),
    path(r'support/faq/new/', WEBviews.faqNew, name='faq-new'),
    path(r'delete-faq/', APIviews.deleteFAQ, name='delete-faq'),

    # MODERATOR
    path(r'moderator/bans/', WEBviews.bans, name='user-bans'),
    path(r'moderator/ban/<str:username>/', WEBviews.banUser, name='user-ban'),
    path(r'moderator/bans/<int:banId>/', WEBviews.banEdit, name='edit-ban'),
    path(r'unban/', APIviews.unban, name='unban'),




    # CHANGELOG
    path(r'changelog/', CLviews.released, name='changelog'),
    path(r'changelog/<int:page>/', CLviews.changelogs, name='changelog'),
    path(r'changelog/upcoming/', CLviews.upcoming, name='changelog-upcoming'),
    path(r'changelog/upcoming/<int:page>/', CLviews.changelogs, name='changelog-upcoming'),
    path(r'changelog/request/', CLviews.request, name='changelog-request'),
]
