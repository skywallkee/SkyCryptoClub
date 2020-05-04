import uuid
import os
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings

from .managers import CustomUserManager

class User(AbstractBaseUser, PermissionsMixin):
    def setId():
        number = User.objects.count()
        if number == None:
            return 1
        else:
            return number + 1

    id = models.BigIntegerField(default=setId)
    publicId = models.UUIDField(primary_key=True, default=uuid.uuid4)
    username = models.CharField(max_length=35, unique=True)
    email = models.EmailField(_('email address'), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    def __str__(self):
        return self.username


class PasswordToken(models.Model):
    def setValid():
        return timezone.now() + timezone.timedelta(minutes=15)
    def setKey():
        import string
        import random
        characters = string.ascii_letters + string.digits + string.punctuation
        stringLength = 34
        return ''.join(random.choice(characters) for i in range(stringLength))
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=35, default=setKey)
    valid_until = models.DateTimeField(default=setValid)

    def __str__(self):
        return self.user.username + " | " + str(self.valid_until)


class TwoFactorLogin(models.Model):
    def setValid():
        return timezone.now() + timezone.timedelta(minutes=15)
    def setKey():
        import string
        import random
        characters = string.ascii_letters + string.digits + string.punctuation
        stringLength = 34
        return ''.join(random.choice(characters) for i in range(stringLength))
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=35, default=setKey)
    valid_until = models.DateTimeField(default=setValid)

    def __str__(self):
        return self.user.username + " | " + str(self.valid_until)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    avatar = models.ImageField(default="default_avatar.jpg")
    xp = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    level = models.BigIntegerField(default=0)
    publicStats = models.BooleanField(default=True)
    publicLevel = models.BooleanField(default=True)
    publicXP = models.BooleanField(default=True)
    publicName = models.BooleanField(default=True)
    
    def __str__(self):
        return self.user.username


class Statistics(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, primary_key=True)
    totalExchangesStarted = models.BigIntegerField(default=0)
    totalExchangesSent = models.BigIntegerField(default=0)

    numberBTCSent = models.DecimalField(max_digits=15, decimal_places=8, default=0)
    amountBTCSent = models.DecimalField(max_digits=15, decimal_places=8, default=0)
    numberBTCReceived = models.DecimalField(max_digits=15, decimal_places=8, default=0)
    amountBTCReceived = models.DecimalField(max_digits=15, decimal_places=8, default=0)

    numberETHSent = models.DecimalField(max_digits=15, decimal_places=8, default=0)
    amountETHSent = models.DecimalField(max_digits=15, decimal_places=8, default=0)
    numberETHReceived = models.DecimalField(max_digits=15, decimal_places=8, default=0)
    amountETHReceived = models.DecimalField(max_digits=15, decimal_places=8, default=0)

    numberLTCSent = models.DecimalField(max_digits=16, decimal_places=8, default=0)
    amountLTCSent = models.DecimalField(max_digits=16, decimal_places=8, default=0)
    numberLTCReceived = models.DecimalField(max_digits=16, decimal_places=8, default=0)
    amountLTCReceived = models.DecimalField(max_digits=16, decimal_places=8, default=0)

    numberXDGSent = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    amountXDGSent = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    numberXDGReceived = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    amountXDGReceived = models.DecimalField(max_digits=20, decimal_places=8, default=0)

    numberBCHSent = models.DecimalField(max_digits=15, decimal_places=8, default=0)
    amountBCHSent = models.DecimalField(max_digits=15, decimal_places=8, default=0)
    numberBCHReceived = models.DecimalField(max_digits=15, decimal_places=8, default=0)
    amountBCHReceived = models.DecimalField(max_digits=15, decimal_places=8, default=0)

    numberXRPSent = models.DecimalField(max_digits=19, decimal_places=8, default=0)
    amountXRPSent = models.DecimalField(max_digits=19, decimal_places=8, default=0)
    numberXRPReceived = models.DecimalField(max_digits=19, decimal_places=8, default=0)
    amountXRPReceived = models.DecimalField(max_digits=19, decimal_places=8, default=0)

    numberTRXSent = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    amountTRXSent = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    numberTRXReceived = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    amountTRXReceived = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    
    def __str__(self):
        return self.profile.user.username


class Role(models.Model):
    def setId():
        number = Role.objects.count()
        if number == None:
            return 1
        else:
            return number + 1

    id = models.BigIntegerField(default=setId, primary_key=True)
    name = models.CharField(max_length=35, default=0)
    color = models.CharField(max_length=7, default="#a8a8a8")
    isDefault = models.BooleanField(default=False)

    # Admin
    adminPanel = models.BooleanField(default=False)
    adminStatistics = models.BooleanField(default=False)
    editMemberships = models.BooleanField(default=False)
    createMemberships = models.BooleanField(default=False)
    deleteMemberships = models.BooleanField(default=False)
    addPlatform = models.BooleanField(default=False)
    editPlatform = models.BooleanField(default=False)
    deletePlatform = models.BooleanField(default=False)
    banUser = models.BooleanField(default=False)
    permanentBan = models.BooleanField(default=False)
    editXP = models.BooleanField(default=False)
    editUserMembership = models.BooleanField(default=False)
    addCurrency = models.BooleanField(default=False)
    editCurrency = models.BooleanField(default=False)
    deleteCurrency = models.BooleanField(default=False)
    addBorrowStatus = models.BooleanField(default=False)
    editBorrowStatus = models.BooleanField(default=False)
    removeBorrowStatus = models.BooleanField(default=False)
    editBorrow = models.BooleanField(default=False)
    addExchangeStatus = models.BooleanField(default=False)
    editExchangeStatus = models.BooleanField(default=False)
    removeExchangeStatus = models.BooleanField(default=False)
    editExchange = models.BooleanField(default=False)
    addFAQCategory = models.BooleanField(default=False)
    editFAQCategory = models.BooleanField(default=False)
    removeFAQCategory = models.BooleanField(default=False)
    approveFAQ = models.BooleanField(default=False)
    addAccount = models.BooleanField(default=False)
    editAccount = models.BooleanField(default=False)
    createRole = models.BooleanField(default=False)
    editRole = models.BooleanField(default=False)
    removeRole = models.BooleanField(default=False)
    assignRole = models.BooleanField(default=False)

    # Moderator
    moderationPanel = models.BooleanField(default=False)
    banExchange = models.BooleanField(default=False)
    banBorrow = models.BooleanField(default=False)
    banLend = models.BooleanField(default=False)
    closeExchange = models.BooleanField(default=False)
    closeBorrow = models.BooleanField(default=False)

    # Support
    viewTickets = models.BooleanField(default=False)
    respondTickets = models.BooleanField(default=False)
    closeTickets = models.BooleanField(default=False)
    addFAQ = models.BooleanField(default=False)
    editFAQ = models.BooleanField(default=False)
    removeFAQ = models.BooleanField(default=False)
    viewUserBorrows = models.BooleanField(default=False)
    viewUserLendings = models.BooleanField(default=False)
    viewUserProfile = models.BooleanField(default=False)
    viewUserExchanges = models.BooleanField(default=False)
    viewExchange = models.BooleanField(default=False)
    viewBorrow = models.BooleanField(default=False)
    viewUserBalance = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name


class UserRole(models.Model):
    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, unique=False, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, unique=False, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("profile", "role")
    
    def __str__(self):
        return self.profile.user.username + " | " + self.role.name


class ProfileBan(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, primary_key=True)
    totalBan = models.BooleanField(default=False, null=False)
    exchangeBan = models.BooleanField(default=False, null=False)
    borrowBan = models.BooleanField(default=False, null=False)
    lendBan = models.BooleanField(default=False, null=False)
    withdrawBan = models.BooleanField(default=False, null=False)
    banDue = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.profile.user.username


class Platform(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=35, null=False, unique=True)
    
    def __str__(self):
        return self.name


class Currency(models.Model):
    name = models.CharField(max_length=10, primary_key=True)
    largeName = models.CharField(max_length=35, null=False)
    
    def __str__(self):
        return self.largeName


class PlatformCurrency(models.Model):
    platform = models.ForeignKey(Platform, null=False, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, null=False, on_delete=models.CASCADE)
    minTip = models.DecimalField(max_digits=21, decimal_places=8, default=0)

    class Meta:
        unique_together = ("platform", "currency")

    def __str__(self):
        return self.platform.name + " | " + self.currency.largeName


class Wallet(models.Model):
    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    store = models.ForeignKey(PlatformCurrency, null=False, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=8, default=0)

    class Meta:
        unique_together = ("profile", "store")
    
    def __str__(self):
        return self.profile.user.username + " | " + self.store.platform.name + " | " + self.store.currency.name


class Account(models.Model):
    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, null=False, on_delete=models.CASCADE)
    username = models.CharField(max_length=35, null=False)
    active = models.BooleanField(default=False)

    class Meta:
        unique_together = ("profile", "platform", "username")
    
    def __str__(self):
        return self.profile.user.username + " | " + self.platform.name + " | " + str(self.active)


class AccountKey(models.Model):
    def setKey():
        import string
        import random
        characters = string.ascii_letters + string.digits
        stringLength = 34
        return ''.join(random.choice(characters) for i in range(stringLength))

    id = models.AutoField(primary_key=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    key = models.CharField(max_length=35, default=setKey)
    
    def __str__(self):
        return self.account.platform.name + " | " + self.account.profile.user.username + " | " + self.account.username + " | " + self.key


class FoundDeposit(models.Model):
    id = models.AutoField(primary_key=True)
    tipId = models.CharField(max_length=40)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("tipId", "account", "platform")
    
    def __str__(self):
        return self.account.username + " | " + self.profile.user.username + " | " + self.platform.name + " | " + self.tipId


class Exchange(models.Model):
    id = models.AutoField(primary_key=True)
    creator = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="creator_user")
    from_currency = models.ForeignKey(PlatformCurrency, on_delete=models.CASCADE, related_name="from_currency")
    from_amount = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    to_currency = models.ForeignKey(PlatformCurrency, on_delete=models.CASCADE, related_name="target_currency")
    to_amount = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    exchanged_by = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL, related_name="exchanger_user")
    
    def __str__(self):
        return self.creator.user.username + " | " + self.from_currency.currency.name + " -> " + self.to_currency.currency.name


class FAQCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=35, null=False, unique=True)
    
    def __str__(self):
        return self.name


class Question(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(FAQCategory, on_delete=models.CASCADE, related_name="category")
    question = models.TextField()
    answer = models.TextField()
    accepted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.category.name + " | " + self.question


def create_user_profile(sender, instance, created, **kwargs):
    Profile.objects.create(user=instance)


def create_profile_role(sender, instance, created, **kwargs):
    profile = Profile.objects.filter(user=instance).first()
    roleList = Role.objects.filter(isDefault=True)
    for role in roleList:
        UserRole.objects.create(profile=profile, role=role)


def create_profile_wallet(sender, instance, created, **kwargs):
    profile = Profile.objects.filter(user=instance).first()
    stores = PlatformCurrency.objects.all()
    for store in stores:
        Wallet.objects.create(profile=profile, store=store, amount=0)


def create_profile_statistics(sender, instance, created, **kwargs):
    profile = Profile.objects.filter(user=instance).first()
    Statistics.objects.create(profile=profile)


def create_user(sender, instance, created, **kwargs):
    if created:
        create_user_profile(sender, instance, created, **kwargs)
        create_profile_role(sender, instance, created, **kwargs)
        create_profile_wallet(sender, instance, created, **kwargs)
        create_profile_statistics(sender, instance, created, **kwargs)


def create_wallets(sender, instance, created, **kwargs):
    if created:
        users = Profile.objects.all()
        for user in users:
            Wallet.objects.create(profile=user, store=instance, amount=0)


def create_key(sender, instance, created, **kwargs):
    if created:
        key = AccountKey.objects.create(account=instance)

post_save.connect(create_user, sender=User)
post_save.connect(create_wallets, sender=PlatformCurrency)
post_save.connect(create_key, sender=Account)