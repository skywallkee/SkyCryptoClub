from django.contrib import admin
from .models import User, Profile, UserRole, Role, ProfileBan, Platform, PlatformCurrency, Currency, \
                    Wallet, Account, PasswordToken, Exchange, ExchangeStatus, TwoFactorLogin, \
                    ExchangeTaxPeer, Question, FAQCategory, FoundDeposit, PublicityBanners, \
                    SupportTicket, SupportCategory, SupportTicketMessage, Languages
from django.contrib.auth.models import Group

admin.site.unregister(Group)

class UserAdmin(admin.ModelAdmin):
    fields = ['publicId', 'username', 'email', 'password', 'is_staff', 'is_active', 'date_joined']

admin.site.register(User, UserAdmin)

class PasswordTokenAdmin(admin.ModelAdmin):
    fields = ['user', 'key', 'valid_until']

admin.site.register(PasswordToken, PasswordTokenAdmin)

class TwoFactorLoginAdmin(admin.ModelAdmin):
    fields = ['user', 'key', 'valid_until']

admin.site.register(TwoFactorLogin, TwoFactorLoginAdmin)


class LanguagesAdmin(admin.ModelAdmin):
    fields = ['name', 'long_name', 'flag']

admin.site.register(Languages, LanguagesAdmin)


class ProfileAdmin(admin.ModelAdmin):
    fields = ['user', 'avatar', 'xp', 'level', 'publicStats', 'publicLevel', 'publicXP', 'publicName', "language"]

admin.site.register(Profile, ProfileAdmin)


class UserRoleAdmin(admin.ModelAdmin):
    fields = ['profile', 'role', 'primary']

admin.site.register(UserRole, UserRoleAdmin)


class RoleAdmin(admin.ModelAdmin):
    fields = ['id', 'name', 'color', 'isDefault',
              'adminPanel', 'adminStatistics',
              'addPlatform',
              'editPlatform', 'deletePlatform', 'banUser',
              'permanentBan',
              'addCurrency', 'editCurrency', 'deleteCurrency',
              'editExchange',
              'addFAQCategory', 'editFAQCategory',
              'removeFAQCategory', 'approveFAQ',
              'editAccount',
              'moderationPanel', 'banExchange',
              'closeExchange',
              'viewTickets', 'respondTickets', 'closeTickets',
              'addFAQ', 'editFAQ', 'removeFAQ']

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
    fields = ['name', 'largeName', 'color', 'icon']

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


class ExchangeTaxPeerAdmin(admin.ModelAdmin):
    fields = ['minAmount', 'maxAmount', 'percentage', 'currency']

admin.site.register(ExchangeTaxPeer, ExchangeTaxPeerAdmin)


class ExchangeStatusAdmin(admin.ModelAdmin):
    fields = ['status', 'color']

admin.site.register(ExchangeStatus, ExchangeStatusAdmin)


class ExchangeAdmin(admin.ModelAdmin):
    fields = ['creator', 'from_currency', 'from_amount', 'to_currency', 'to_amount', 'exchanged_by', 'ratio', 'status', 'creator_amount', 'exchanger_amount', 'taxCreator', 'taxExchanger']

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


class SupportTicketAdmin(admin.ModelAdmin):
    fields = ['creator', 'title', 'category', 'last_replied', 'created_at', 'closed']

admin.site.register(SupportTicket, SupportTicketAdmin)


class SupportCategoryAdmin(admin.ModelAdmin):
    fields = ['order', 'name']

admin.site.register(SupportCategory, SupportCategoryAdmin)


class SupportTicketMessageAdmin(admin.ModelAdmin):
    fields = ['ticket', 'sender', 'message', 'sent_at']

admin.site.register(SupportTicketMessage, SupportTicketMessageAdmin)
