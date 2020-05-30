from django.contrib import admin
from .models import User, Profile, UserRole, Role, ProfileBan, Platform, PlatformCurrency, Currency, \
                    Wallet, Account, AccountKey, PasswordToken, Exchange, TwoFactorLogin, \
                    Question, FAQCategory, Statistics, FoundDeposit, PublicityBanners
from django.contrib.auth.models import Group

admin.site.unregister(Group)

class UserAdmin(admin.ModelAdmin):
    fields = ['id', 'publicId', 'username', 'email', 'password', 'is_staff', 'is_active', 'date_joined']

admin.site.register(User, UserAdmin)

class PasswordTokenAdmin(admin.ModelAdmin):
    fields = ['user', 'key', 'valid_until']

admin.site.register(PasswordToken, PasswordTokenAdmin)

class TwoFactorLoginAdmin(admin.ModelAdmin):
    fields = ['user', 'key', 'valid_until']

admin.site.register(TwoFactorLogin, TwoFactorLoginAdmin)


class ProfileAdmin(admin.ModelAdmin):
    fields = ['user', 'avatar', 'xp', 'level', 'publicStats', 'publicLevel', 'publicXP', 'publicName']

admin.site.register(Profile, ProfileAdmin)


class StatisticsAdmin(admin.ModelAdmin):
    fields = ['profile', 'numberBTCSent', 'amountBTCSent', 'numberBTCReceived', 'amountBTCReceived', 
            'numberETHSent', 'amountETHSent', 'numberETHReceived', 'amountETHReceived', 
            'numberLTCSent', 'amountLTCSent', 'numberLTCReceived', 'amountLTCReceived', 
            'numberXDGSent', 'amountXDGSent', 'numberXDGReceived', 'amountXDGReceived', 
            'numberBCHSent', 'amountBCHSent', 'numberBCHReceived', 'amountBCHReceived', 
            'numberXRPSent', 'amountXRPSent', 'numberXRPReceived', 'amountXRPReceived', 
            'numberTRXSent', 'amountTRXSent', 'numberTRXReceived', 'amountTRXReceived'
            ]

admin.site.register(Statistics, StatisticsAdmin)


class UserRoleAdmin(admin.ModelAdmin):
    fields = ['profile', 'role', 'primary']

admin.site.register(UserRole, UserRoleAdmin)


class RoleAdmin(admin.ModelAdmin):
    fields = ['id', 'name', 'color', 'isDefault',
              'adminPanel', 'adminStatistics',
              'editMemberships', 'createMemberships',
              'deleteMemberships', 'addPlatform',
              'editPlatform', 'deletePlatform', 'banUser',
              'permanentBan', 'editXP', 'editUserMembership',
              'addCurrency', 'editCurrency', 'deleteCurrency',
              'addBorrowStatus', 'editBorrowStatus',
              'removeBorrowStatus', 'editBorrow', 
              'addExchangeStatus', 'editExchangeStatus',
              'removeExchangeStatus', 'editExchange',
              'addFAQCategory', 'editFAQCategory',
              'removeFAQCategory', 'approveFAQ',
              'addAccount', 'editAccount', 'createRole',
              'editRole', 'removeRole', 'assignRole',
              'moderationPanel', 'banExchange', 'banBorrow',
              'banLend', 'closeExchange', 'closeBorrow',
              'viewTickets', 'respondTickets', 'closeTickets',
              'addFAQ', 'editFAQ', 'removeFAQ', 'viewUserBorrows',
              'viewUserLendings', 'viewUserProfile', 'viewUserExchanges',
              'viewExchange', 'viewBorrow', 'viewUserBalance']

admin.site.register(Role, RoleAdmin)


class ProfileBanAdmin(admin.ModelAdmin):
    fields = ['profile', 'totalBan', 'exchangeBan', 'borrowBan', 'lendBan', 'banDue']

admin.site.register(ProfileBan, ProfileBanAdmin)


class PlatformAdmin(admin.ModelAdmin):
    fields = ['name']

admin.site.register(Platform, PlatformAdmin)


class PlatformCurrencyAdmin(admin.ModelAdmin):
    fields = ['platform', 'currency']

admin.site.register(PlatformCurrency, PlatformCurrencyAdmin)


class CurrencyAdmin(admin.ModelAdmin):
    fields = ['name', 'largeName']

admin.site.register(Currency, CurrencyAdmin)


class WalletAdmin(admin.ModelAdmin):
    fields = ['profile', 'store', 'amount']

admin.site.register(Wallet, WalletAdmin)


class AccountAdmin(admin.ModelAdmin):
    fields = ['profile', 'platform', 'username', 'active']

admin.site.register(Account, AccountAdmin)


class FoundDepositAdmin(admin.ModelAdmin):
    fields = ['tipId', 'profile', 'account', 'platform']

admin.site.register(FoundDeposit, FoundDepositAdmin)


class AccountKeyAdmin(admin.ModelAdmin):
    fields = ['account', 'key']

admin.site.register(AccountKey, AccountKeyAdmin)


class ExchangeAdmin(admin.ModelAdmin):
    fields = ['creator', 'from_currency', 'from_amount', 'to_currency', 'to_amount', 'exchanged_by']

admin.site.register(Exchange, ExchangeAdmin)


class FAQCategoryAdmin(admin.ModelAdmin):
    fields = ['name']

admin.site.register(FAQCategory, FAQCategoryAdmin)


class QuestionAdmin(admin.ModelAdmin):
    fields = ['category', 'question', 'answer', 'accepted']

admin.site.register(Question, QuestionAdmin)


class PublicityBannersAdmin(admin.ModelAdmin):
    fields = ['image', 'imageType']

admin.site.register(PublicityBanners, PublicityBannersAdmin)