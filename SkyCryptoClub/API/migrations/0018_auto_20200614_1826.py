# Generated by Django 3.0.7 on 2020-06-14 18:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0017_delete_statistics'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='role',
            name='addAccount',
        ),
        migrations.RemoveField(
            model_name='role',
            name='addBorrowStatus',
        ),
        migrations.RemoveField(
            model_name='role',
            name='addExchangeStatus',
        ),
        migrations.RemoveField(
            model_name='role',
            name='assignRole',
        ),
        migrations.RemoveField(
            model_name='role',
            name='banBorrow',
        ),
        migrations.RemoveField(
            model_name='role',
            name='banLend',
        ),
        migrations.RemoveField(
            model_name='role',
            name='closeBorrow',
        ),
        migrations.RemoveField(
            model_name='role',
            name='createMemberships',
        ),
        migrations.RemoveField(
            model_name='role',
            name='createRole',
        ),
        migrations.RemoveField(
            model_name='role',
            name='deleteMemberships',
        ),
        migrations.RemoveField(
            model_name='role',
            name='editBorrow',
        ),
        migrations.RemoveField(
            model_name='role',
            name='editBorrowStatus',
        ),
        migrations.RemoveField(
            model_name='role',
            name='editExchangeStatus',
        ),
        migrations.RemoveField(
            model_name='role',
            name='editMemberships',
        ),
        migrations.RemoveField(
            model_name='role',
            name='editRole',
        ),
        migrations.RemoveField(
            model_name='role',
            name='editUserMembership',
        ),
        migrations.RemoveField(
            model_name='role',
            name='editXP',
        ),
        migrations.RemoveField(
            model_name='role',
            name='removeBorrowStatus',
        ),
        migrations.RemoveField(
            model_name='role',
            name='removeExchangeStatus',
        ),
        migrations.RemoveField(
            model_name='role',
            name='removeRole',
        ),
        migrations.RemoveField(
            model_name='role',
            name='viewBorrow',
        ),
        migrations.RemoveField(
            model_name='role',
            name='viewExchange',
        ),
        migrations.RemoveField(
            model_name='role',
            name='viewUserBalance',
        ),
        migrations.RemoveField(
            model_name='role',
            name='viewUserBorrows',
        ),
        migrations.RemoveField(
            model_name='role',
            name='viewUserExchanges',
        ),
        migrations.RemoveField(
            model_name='role',
            name='viewUserLendings',
        ),
        migrations.RemoveField(
            model_name='role',
            name='viewUserProfile',
        ),
    ]
