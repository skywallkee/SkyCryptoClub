import uuid
import os
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model

from .managers import CustomUserManager


class IPBan(models.Model):
    ipAddress = models.CharField(max_length=16, primary_key=True)
    due = models.DateTimeField(null=True, blank=True)
    permanent = models.BooleanField(default=False)

    def __str__(self):
        permanent = "PERMANENT" if self.permanent else "TEMPORARY"
        return self.ipAddress + " " + str(self.due) + " | " + permanent


class User(AbstractBaseUser, PermissionsMixin):
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
        characters = string.ascii_letters + string.digits
        stringLength = 34
        return ''.join(random.choice(characters) for i in range(stringLength))
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=35, default=setKey)
    valid_until = models.DateTimeField(default=setValid)

    def __str__(self):
        return self.user.username + " | " + str(self.valid_until)


def avatar_upload(instance, filename):
    avatar_name = instance.user.username + "." + filename.split(".")[-1]
    full_path = os.path.join(settings.MEDIA_ROOT, "avatars/", avatar_name)
    if os.path.exists(full_path):
        os.remove(full_path)
    return avatar_name


def flag_upload(instance, filename):
    flag_name = instance.name + "." + filename.split(".")[-1]
    full_path = os.path.join(settings.MEDIA_ROOT, "flags/", flag_name)
    if os.path.exists(full_path):
        os.remove(full_path)
    return flag_name


class Languages(models.Model):
    name = models.CharField(max_length=3, primary_key=True)
    long_name = models.CharField(max_length=30)
    flag = models.ImageField(null=True, upload_to=flag_upload)

    def __str__(self):
        return self.long_name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    avatar = models.ImageField(default="default_avatar.jpg", upload_to=avatar_upload)
    xp = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    level = models.BigIntegerField(default=0)
    publicStats = models.BooleanField(default=True)
    publicLevel = models.BooleanField(default=True)
    publicXP = models.BooleanField(default=True)
    publicName = models.BooleanField(default=True)
    language = models.ForeignKey(Languages, null=True, default="en", on_delete=models.SET_DEFAULT)
    twofactor = models.BooleanField(default=True)
    
    def __str__(self):
        return self.user.username

class Invitation(models.Model):
    code = models.CharField(max_length=64, primary_key=True)
    creator = models.ForeignKey(Profile, on_delete=models.CASCADE, unique=False)
    clicks = models.BigIntegerField(default=0)
    registrations = models.BigIntegerField(default=0)
    limit = models.BigIntegerField(default=-1)

    def __str__(self):
        return self.creator.user.username + " | " + self.code


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
    addPlatform = models.BooleanField(default=False)
    editPlatform = models.BooleanField(default=False)
    deletePlatform = models.BooleanField(default=False)
    permanentBan = models.BooleanField(default=False)
    addCurrency = models.BooleanField(default=False)
    editCurrency = models.BooleanField(default=False)
    deleteCurrency = models.BooleanField(default=False)
    editExchange = models.BooleanField(default=False)
    addFAQCategory = models.BooleanField(default=False)
    editFAQCategory = models.BooleanField(default=False)
    removeFAQCategory = models.BooleanField(default=False)
    approveFAQ = models.BooleanField(default=False)
    editAccount = models.BooleanField(default=False)

    # Moderator
    moderationPanel = models.BooleanField(default=False)
    banUser = models.BooleanField(default=False)
    banExchange = models.BooleanField(default=False)
    banWithdraw = models.BooleanField(default=False)
    closeExchange = models.BooleanField(default=False)
    unban = models.BooleanField(default=False)

    # Support
    viewTickets = models.BooleanField(default=False)
    respondTickets = models.BooleanField(default=False)
    closeTickets = models.BooleanField(default=False)
    addFAQ = models.BooleanField(default=False)
    editFAQ = models.BooleanField(default=False)
    removeFAQ = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name


class UserRole(models.Model):
    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    primary = models.BooleanField(default=True)

    class Meta:
        unique_together = ("profile", "role")
    
    def __str__(self):
        return self.profile.user.username + " | " + self.role.name


class ProfileBan(models.Model):
    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    totalBan = models.BooleanField(default=False, null=False)
    exchangeBan = models.BooleanField(default=False, null=False)
    borrowBan = models.BooleanField(default=False, null=False)
    lendBan = models.BooleanField(default=False, null=False)
    withdrawBan = models.BooleanField(default=False, null=False)
    reason = models.TextField(default="", null=False)
    bannedBy = models.ForeignKey(Profile, default=None, on_delete=models.CASCADE, related_name="bannedBy")
    banDue = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.profile.user.username


class Platform(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=35, null=False, unique=True)
    
    def __str__(self):
        return self.name


def currency_icon_upload(instance, filename):
    currency_name = instance.name + "." + filename.split(".")[-1]
    full_path = os.path.join(settings.MEDIA_ROOT, currency_name)
    if os.path.exists(full_path):
        os.remove(full_path)
    return currency_name


class Currency(models.Model):
    name = models.CharField(max_length=10, primary_key=True)
    largeName = models.CharField(max_length=35, blank=False)
    color = models.CharField(max_length=7, blank=False, default="#000000")
    icon = models.ImageField(default="default_crypto.png", upload_to=currency_icon_upload)

    
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
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("profile", "platform", "username")
    
    def __str__(self):
        return self.username + " | " + self.platform.name


class FoundDeposit(models.Model):
    id = models.AutoField(primary_key=True)
    tipId = models.CharField(max_length=40)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("tipId", "account")
    
    def __str__(self):
        return self.account.username + " | " + self.profile.user.username + " | " + self.tipId


class Withdrawal(models.Model):
    id = models.AutoField(primary_key=True)
    tipId = models.CharField(max_length=40)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("tipId", "account")
    
    def __str__(self):
        return self.account.username + " | " + self.profile.user.username + " | " + self.tipId


class ExchangeStatus(models.Model):
    status = models.CharField(max_length=40, primary_key=True)
    color = models.CharField(max_length=7, default="#a8a8a8")

    def __str__(self):
        return self.status


class ExchangeTaxPeer(models.Model):
    minAmount = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    maxAmount = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    percentage = models.DecimalField(max_digits=6, decimal_places=4, default=0)
    currency = models.ForeignKey(Currency, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return "[" + str(self.minAmount) + "; " + str(self.maxAmount) + "] " + str(self.percentage) + "% " + self.currency.name


class Exchange(models.Model):
    eid = models.AutoField(primary_key=True)
    creator = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="creator_user")
    from_currency = models.ForeignKey(PlatformCurrency, on_delete=models.CASCADE, related_name="from_currency")
    from_amount = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    to_currency = models.ForeignKey(PlatformCurrency, on_delete=models.CASCADE, related_name="target_currency")
    to_amount = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    exchanged_by = models.ForeignKey(Profile, null=True, blank=True, on_delete=models.SET_NULL, related_name="exchanger_user")
    creator_amount = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    exchanger_amount = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    ratio = models.DecimalField(max_digits=20, decimal_places = 8, default=0)
    status = models.ForeignKey(ExchangeStatus, null=True, on_delete=models.CASCADE)
    taxCreator = models.ForeignKey(ExchangeTaxPeer, null=True, on_delete=models.SET_NULL, related_name="creator_tax")
    taxExchanger = models.ForeignKey(ExchangeTaxPeer, null=True, on_delete=models.SET_NULL, related_name="exchanger_tax")
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.creator.user.username + " | " + self.from_currency.currency.name + " -> " + self.to_currency.currency.name


class FAQCategory(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.IntegerField(unique=True, null=True)
    name = models.CharField(max_length=35, null=False, unique=True)
    
    def __str__(self):
        return str(self.order) + ". " + self.name


class Question(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(FAQCategory, on_delete=models.CASCADE, related_name="category")
    question = models.TextField()
    answer = models.TextField()
    accepted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.category.name + " | " + self.question

BANNER_CHOICES = (
    ("large", "large"),
    ("medium", "medium"),
    ("small", "small"),
)

class PublicityBanners(models.Model):
    image = models.ImageField(upload_to="partners/")
    imageType = models.CharField(max_length = 35, choices = BANNER_CHOICES, default = "large")
    
    def __str__(self):
        return self.image.name


class SupportCategory(models.Model):
    name = models.CharField(max_length = 35, primary_key=True)
    order = models.IntegerField(unique=True, null=True)

    def __str__(self):
        return str(self.order) + ". " + self.name


class SupportTicket(models.Model):
    ticketId = models.AutoField(primary_key=True)
    creator = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL, related_name="creator")
    title = models.CharField(max_length = 60, null=False, blank=False, default="Title")
    category = models.ForeignKey(SupportCategory, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(default=timezone.now)
    last_replied = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL, related_name="last_replier")
    closed = models.BooleanField(default=False)

    def __str__(self):
        return self.creator.user.username + " | " + self.title + " | " + self.category.name


class SupportTicketMessage(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE)
    sender = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL)
    message = models.TextField(blank=False, null=False, default="Message")
    sent_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.sender.user.username + " -> " + self.ticket.title


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


def create_user(sender, instance, created, **kwargs):
    if created:
        create_user_profile(sender, instance, created, **kwargs)
        create_profile_role(sender, instance, created, **kwargs)
        create_profile_wallet(sender, instance, created, **kwargs)


def create_wallets(sender, instance, created, **kwargs):
    if created:
        users = Profile.objects.all()
        for user in users:
            Wallet.objects.create(profile=user, store=instance, amount=0)

post_save.connect(create_user, sender=User)
post_save.connect(create_wallets, sender=PlatformCurrency)