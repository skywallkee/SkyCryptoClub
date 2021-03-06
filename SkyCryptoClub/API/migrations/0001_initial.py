# Generated by Django 3.0.8 on 2020-07-11 18:19

import SkyCryptoClub.API.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('name', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('largeName', models.CharField(max_length=35)),
                ('color', models.CharField(default='#000000', max_length=7)),
                ('icon', models.ImageField(default='default_crypto.png', upload_to=SkyCryptoClub.API.models.currency_icon_upload)),
            ],
        ),
        migrations.CreateModel(
            name='ExchangeStatus',
            fields=[
                ('status', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('color', models.CharField(default='#a8a8a8', max_length=7)),
            ],
        ),
        migrations.CreateModel(
            name='FAQCategory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=35, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Languages',
            fields=[
                ('name', models.CharField(max_length=3, primary_key=True, serialize=False)),
                ('long_name', models.CharField(max_length=30)),
                ('flag', models.ImageField(null=True, upload_to=SkyCryptoClub.API.models.flag_upload)),
            ],
        ),
        migrations.CreateModel(
            name='Platform',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=35, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='PlatformCurrency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('minTip', models.DecimalField(decimal_places=8, default=0, max_digits=21)),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.Currency')),
                ('platform', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.Platform')),
            ],
            options={
                'unique_together': {('platform', 'currency')},
            },
        ),
        migrations.CreateModel(
            name='PublicityBanners',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='partners/')),
                ('imageType', models.CharField(choices=[('large', 'large'), ('medium', 'medium'), ('small', 'small')], default='large', max_length=35)),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigIntegerField(default=SkyCryptoClub.API.models.Role.setId, primary_key=True, serialize=False)),
                ('name', models.CharField(default=0, max_length=35)),
                ('color', models.CharField(default='#a8a8a8', max_length=7)),
                ('isDefault', models.BooleanField(default=False)),
                ('adminPanel', models.BooleanField(default=False)),
                ('adminStatistics', models.BooleanField(default=False)),
                ('addPlatform', models.BooleanField(default=False)),
                ('editPlatform', models.BooleanField(default=False)),
                ('deletePlatform', models.BooleanField(default=False)),
                ('permanentBan', models.BooleanField(default=False)),
                ('addCurrency', models.BooleanField(default=False)),
                ('editCurrency', models.BooleanField(default=False)),
                ('deleteCurrency', models.BooleanField(default=False)),
                ('editExchange', models.BooleanField(default=False)),
                ('addFAQCategory', models.BooleanField(default=False)),
                ('editFAQCategory', models.BooleanField(default=False)),
                ('removeFAQCategory', models.BooleanField(default=False)),
                ('approveFAQ', models.BooleanField(default=False)),
                ('editAccount', models.BooleanField(default=False)),
                ('moderationPanel', models.BooleanField(default=False)),
                ('banUser', models.BooleanField(default=False)),
                ('banExchange', models.BooleanField(default=False)),
                ('banWithdraw', models.BooleanField(default=False)),
                ('closeExchange', models.BooleanField(default=False)),
                ('unban', models.BooleanField(default=False)),
                ('viewTickets', models.BooleanField(default=False)),
                ('respondTickets', models.BooleanField(default=False)),
                ('closeTickets', models.BooleanField(default=False)),
                ('addFAQ', models.BooleanField(default=False)),
                ('editFAQ', models.BooleanField(default=False)),
                ('removeFAQ', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='SupportCategory',
            fields=[
                ('name', models.CharField(max_length=35, primary_key=True, serialize=False)),
                ('order', models.IntegerField(null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='SupportTicket',
            fields=[
                ('ticketId', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(default='Title', max_length=60)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('closed', models.BooleanField(default=False)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='API.SupportCategory')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('publicId', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=35, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('avatar', models.ImageField(default='default_avatar.jpg', upload_to=SkyCryptoClub.API.models.avatar_upload)),
                ('xp', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('level', models.BigIntegerField(default=0)),
                ('publicStats', models.BooleanField(default=True)),
                ('publicLevel', models.BooleanField(default=True)),
                ('publicXP', models.BooleanField(default=True)),
                ('publicName', models.BooleanField(default=True)),
                ('twofactor', models.BooleanField(default=True)),
                ('language', models.ForeignKey(default='en', null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='API.Languages')),
            ],
        ),
        migrations.CreateModel(
            name='TwoFactorLogin',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('key', models.CharField(default=SkyCryptoClub.API.models.TwoFactorLogin.setKey, max_length=35)),
                ('valid_until', models.DateTimeField(default=SkyCryptoClub.API.models.TwoFactorLogin.setValid)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('question', models.TextField()),
                ('answer', models.TextField()),
                ('accepted', models.BooleanField(default=False)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='category', to='API.FAQCategory')),
            ],
        ),
        migrations.CreateModel(
            name='PasswordToken',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('key', models.CharField(default=SkyCryptoClub.API.models.PasswordToken.setKey, max_length=35)),
                ('valid_until', models.DateTimeField(default=SkyCryptoClub.API.models.PasswordToken.setValid)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ExchangeTaxPeer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('minAmount', models.DecimalField(decimal_places=8, default=0, max_digits=20)),
                ('maxAmount', models.DecimalField(decimal_places=8, default=0, max_digits=20)),
                ('percentage', models.DecimalField(decimal_places=4, default=0, max_digits=6)),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.Currency')),
            ],
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=35)),
                ('active', models.BooleanField(default=True)),
                ('platform', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.Platform')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.Profile')),
            ],
            options={
                'unique_together': {('profile', 'platform', 'username')},
            },
        ),
        migrations.CreateModel(
            name='SupportTicketMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(default='Message')),
                ('sent_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.SupportTicket')),
                ('sender', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='API.Profile')),
            ],
        ),
        migrations.AddField(
            model_name='supportticket',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator', to='API.Profile'),
        ),
        migrations.AddField(
            model_name='supportticket',
            name='last_replied',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='last_replier', to='API.Profile'),
        ),
        migrations.CreateModel(
            name='ProfileBan',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('totalBan', models.BooleanField(default=False)),
                ('exchangeBan', models.BooleanField(default=False)),
                ('borrowBan', models.BooleanField(default=False)),
                ('lendBan', models.BooleanField(default=False)),
                ('withdrawBan', models.BooleanField(default=False)),
                ('reason', models.TextField(default='')),
                ('banDue', models.DateTimeField(default=django.utils.timezone.now)),
                ('bannedBy', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='bannedBy', to='API.Profile')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('code', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('clicks', models.BigIntegerField(default=0)),
                ('registrations', models.BigIntegerField(default=0)),
                ('limit', models.BigIntegerField(default=-1)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='Exchange',
            fields=[
                ('eid', models.AutoField(primary_key=True, serialize=False)),
                ('from_amount', models.DecimalField(decimal_places=8, default=0, max_digits=20)),
                ('to_amount', models.DecimalField(decimal_places=8, default=0, max_digits=20)),
                ('creator_amount', models.DecimalField(decimal_places=8, default=0, max_digits=20)),
                ('exchanger_amount', models.DecimalField(decimal_places=8, default=0, max_digits=20)),
                ('ratio', models.DecimalField(decimal_places=8, default=0, max_digits=20)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('from_currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_currency', to='API.PlatformCurrency')),
                ('status', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='API.ExchangeStatus')),
                ('taxCreator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_tax', to='API.ExchangeTaxPeer')),
                ('taxExchanger', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exchanger_tax', to='API.ExchangeTaxPeer')),
                ('to_currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='target_currency', to='API.PlatformCurrency')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='creator_user', to='API.Profile')),
                ('exchanged_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exchanger_user', to='API.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='Withdrawal',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('tipId', models.CharField(max_length=40)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.Account')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.Profile')),
            ],
            options={
                'unique_together': {('tipId', 'account')},
            },
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=8, default=0, max_digits=20)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.PlatformCurrency')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.Profile')),
            ],
            options={
                'unique_together': {('profile', 'store')},
            },
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('primary', models.BooleanField(default=True)),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.Role')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.Profile')),
            ],
            options={
                'unique_together': {('profile', 'role')},
            },
        ),
        migrations.CreateModel(
            name='FoundDeposit',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('tipId', models.CharField(max_length=40)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.Account')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.Profile')),
            ],
            options={
                'unique_together': {('tipId', 'account')},
            },
        ),
    ]
