from .models import User, Profile, UserRole, Role, ProfileBan, Platform, PlatformCurrency, Currency, \
                    Wallet, Account, AccountKey, PasswordToken, Exchange, TwoFactorLogin, \
                    FAQCategory, Question, Statistics, PublicityBanners
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    publicId = serializers.ReadOnlyField()
    last_password_reset = serializers.ReadOnlyField()
    date_joined = serializers.ReadOnlyField()
    class Meta:
        model = User
        fields = ['url', 'publicId', 'username', 'email', 'password', 
                  'is_staff', 'is_active', 'last_password_reset', 
                  'date_joined']


class PasswordTokenSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(view_name='user-detail', queryset=User.objects.all())
    class Meta:
        model = PasswordToken
        fields = ['url', 'user', 'key', 'valid_until']


class TwoFactorLoginSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(view_name='user-detail', queryset=User.objects.all())
    class Meta:
        model = PasswordToken
        fields = ['url', 'user', 'key', 'valid_until']


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True)
    class Meta:
        model = Profile
        fields = ['url', 'user', 'avatar', 'xp', 'publicStats', 'publicLevel', 'publicXP', 'publicName']


class StatisticsSerializer(serializers.HyperlinkedModelSerializer):
    profile = serializers.HyperlinkedRelatedField(view_name='profile-detail', queryset=Profile.objects.all())
    class Meta:
        model = Statistics
        fields = ['profile', 'numberBTCSent', 'amountBTCSent', 'numberBTCReceived', 'amountBTCReceived', 
            'numberETHSent', 'amountETHSent', 'numberETHReceived', 'amountETHReceived', 
            'numberLTCSent', 'amountLTCSent', 'numberLTCReceived', 'amountLTCReceived', 
            'numberXDGSent', 'amountXDGSent', 'numberXDGReceived', 'amountXDGReceived', 
            'numberBCHSent', 'amountBCHSent', 'numberBCHReceived', 'amountBCHReceived', 
            'numberXRPSent', 'amountXRPSent', 'numberXRPReceived', 'amountXRPReceived', 
            'numberTRXSent', 'amountTRXSent', 'numberTRXReceived', 'amountTRXReceived'
            ]


class UserRoleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserRole
        fields = ['url', 'profile', 'role']


class RoleSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    class Meta:
        model = Role
        fields = ['url', 'id', 'name', 'color', 'isDefault',
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


class ProfileBanSerializer(serializers.HyperlinkedModelSerializer):
    profile = serializers.HyperlinkedRelatedField(view_name='profile-detail', queryset=Profile.objects.all())
    class Meta:
        model = ProfileBan
        fields = ['url', 'profile', 'totalBan', 'exchangeBan', 'borrowBan', 'lendBan', 'banDue']


class PlatformSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Platform
        fields = ['url', 'name']


class PlatformCurrencySerializer(serializers.HyperlinkedModelSerializer):
    platform = serializers.HyperlinkedRelatedField(view_name='platform-detail', queryset=Platform.objects.all())
    currency = serializers.HyperlinkedRelatedField(view_name='currency-detail', queryset=Currency.objects.all())
    class Meta:
        model = PlatformCurrency
        fields = ['url', 'platform', 'currency']


class CurrencySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Currency
        fields = ['url', 'name', 'largeName']


class WalletSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Wallet
        fields = ['url', 'profile', 'store', 'amount']


class AccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Account
        fields = ['url', 'profile', 'platform', 'username', 'active']


class AccountKeySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AccountKey
        fields = ['url', 'account', 'key']


class ExchangeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Exchange
        fields = ['url', 'creator', 'from_currency', 'from_amount', 'to_currency', 'to_amount', 'exchanged_by']


class FAQCategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FAQCategory
        fields = ['url', 'name']


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    category = serializers.HyperlinkedRelatedField(view_name='faqcategory-detail', queryset=FAQCategory.objects.all())
    class Meta:
        model = Question
        fields = ['url', 'category', 'question', 'answer', 'accepted']


class PublicityBannersSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PublicityBanners
        fields = ['image', 'imageType']