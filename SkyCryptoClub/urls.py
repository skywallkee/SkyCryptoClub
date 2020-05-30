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

router = routers.DefaultRouter()
router.register(r'users', APIviews.UserViewSet)
router.register(r'passwordtokens', APIviews.PasswordTokenViewSet)
router.register(r'twofactors', APIviews.TwoFactorLoginViewSet)
router.register(r'profiles', APIviews.ProfileViewSet)
router.register(r'statistics', APIviews.StatisticsViewSet)
router.register(r'userroles', APIviews.UserRoleViewSet)
router.register(r'roles', APIviews.RoleViewSet)
router.register(r'profilebans', APIviews.ProfileBanViewSet)
router.register(r'platforms', APIviews.PlatformViewSet)
router.register(r'currencies', APIviews.CurrencyViewSet)
router.register(r'platformcurrencies', APIviews.PlatformCurrencyViewSet)
router.register(r'wallets', APIviews.WalletViewSet)
router.register(r'accounts', APIviews.AccountViewSet)
router.register(r'accountkeys', APIviews.AccountKeyViewSet)
router.register(r'exchanges', APIviews.ExchangeViewSet)
router.register(r'faqcategories', APIviews.FAQCategoryViewSet)
router.register(r'questions', APIviews.QuestionViewSet)


urlpatterns = [
    path(r'endpoints/', include(router.urls)),
    path(r'api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path(r'check-login/', APIviews.user_login, name='check-login'),
    path(r'check-tfa/', APIviews.check_tfa, name='check-tfa'),
    path(r'get-balances/', APIviews.get_balances, name='get-balances'),
    path(r'get-platform-currencies/', APIviews.get_platform_currencies, name='get-platform-currencies'),
    path(r'get-available-balance/', APIviews.get_available_balance, name='get-available-balance'),
    path(r'reload-balance/', APIviews.reload_balance, name='reload-balance'),
    path(r'withdraw/', APIviews.withdraw, name='withdraw'),
    path(r'get-platform-accounts/', APIviews.get_platform_accounts, name='get-platform-accounts'),
    path(r'admin_tools/', include('admin_tools.urls')),
    path(r'admin/', admin.site.urls),
    path(r'login/', WEBviews.user_login, name='login'),
    path(r'logout/', auth_views.LogoutView.as_view(), name='logout'),
    path(r'register/', WEBviews.user_register, name='register'),
    path(r'recover/', WEBviews.recover_password, name='recover-password'),
    path(r'faq/', WEBviews.faq, name='faq'),
    path(r'terms/', WEBviews.terms, name='terms'),
    path(r'contact/', WEBviews.contact, name='contact'),
    path(r'dashboard/', WEBviews.dashboard, name='dashboard'),
    path(r'dashboard/<str:username>/', WEBviews.dashboard_user, name='dashboard_user'),
    path(r'settings/', WEBviews.settings, name='settings'),
    path(r'settings/privacy/', WEBviews.privacy, name='privacy'),
    path(r'settings/linked/', WEBviews.linked, name='linked'),
    path('', WEBviews.index, name='index'),
]
