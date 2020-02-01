import click, uuid
from werkzeug.security import generate_password_hash
from flask.cli import with_appcontext

import time
from datetime import datetime, date, time, timedelta

from .extensions import db
from .models import User, Platform, Account, Membership, Role,\
    UserRole, Profile, Wallet, Ignored, ProfileMembership, Currency, \
    BorrowStatus, Borrow, ExchangeStatus, Exchange, FAQCategory, FAQ, \
    BannedProfile, BanDue

@click.command(name='create_tables')
@with_appcontext
def create_tables():
    db.create_all()
    # Defaults
    adminUser = User(publicId=str(uuid.uuid4()), username="Admin", password=generate_password_hash("Admin", "sha256"), email="contact@skycrypto.club")
    adminRole = Role(name="Admin", color="red", defaultR=True, admin_panel=True, admin_statistics=True,\
        edit_memberships=True, create_memberships=True, delete_memberships=True, add_platform=True,\
        edit_platform=True, delete_platform=True, ban_user=True, edit_xp=True, edit_user_membership=True,\
        add_currency=True, edit_currency=True, delete_currency=True, add_borrow_status=True,\
        edit_borrow_status=True, remove_borrow_status=True, edit_borrow=True, add_exchange_status=True,\
        edit_exchange_status=True, remove_exchange_status=True, edit_exchange=True, add_faq_category=True,\
        edit_faq_category=True, remove_faq_category=True, add_account=True, edit_account=True, assign_role=True,\
        moderation_panel=True, ban_exchange=True, ban_borrow=True, ban_lend=True, edit_name=True, add_ignored=True,\
        remove_ignored=True, close_exchange=True, close_borrow=True, support_panel=True, view_tickets=True,\
        respond_tickets=True, close_tickets=True, reopen_tickets=True, add_faq=True, edit_faq=True, remove_faq=True,\
        view_user_borrows=True, view_user_lendings=True, view_user_profile=True, view_user_exchanges=True,\
        view_exchange=True, view_borrow=True, view_user_balance=True, delete_account=True)
    adminUserRole = UserRole(userId=adminUser.publicId, role=adminRole.name)
    stake = Platform(name="Stake")
    currency = Currency(name="btc", large_name="Bitcoin", platform="Stake")
    noMembership = Membership(name="None", color="gray", price=0, can_exchange=True, can_borrow=False, can_lend=False,\
        exchange_small_fee=0.07, exchange_large_fee=0.05, exchange_limit=0.6, borrow_base_fee=0.02, borrow_daily_fee=0.01,\
        borrow_grace_fee=0.01, minimum_interest=0.1, max_borrow_days=7, max_grace_days=7, grace_penalty=0.05,\
        max_borrow_amount=0.6, lend_first_fee=1, lend_daily_fee=1, defaultM=True)
    adminUserProfile = Profile(userId=adminUser.publicId)
    adminProfileWallet = Wallet(userId=adminUserProfile.userId, currency="btc", amount=0.0)
    adminUserMembership = ProfileMembership(userId=adminUserProfile.userId, membership=noMembership.name)

    dummyUser1 = User(publicId=str(uuid.uuid4()), username="D1", password=generate_password_hash("D1", "sha256"), email="d1@skycrypto.club")
    dummyUser2 = User(publicId=str(uuid.uuid4()), username="D2", password=generate_password_hash("D2", "sha256"), email="d2@skycrypto.club")
    dummyUser3 = User(publicId=str(uuid.uuid4()), username="D3", password=generate_password_hash("D3", "sha256"), email="d3@skycrypto.club")
    dummyUser4 = User(publicId=str(uuid.uuid4()), username="D4", password=generate_password_hash("D4", "sha256"), email="d4@skycrypto.club")
    dummyUser5 = User(publicId=str(uuid.uuid4()), username="D5", password=generate_password_hash("D5", "sha256"), email="d5@skycrypto.club")
    dummyUser1Profile = Profile(userId=dummyUser1.publicId)
    dummyUser2Profile = Profile(userId=dummyUser2.publicId)
    dummyUser3Profile = Profile(userId=dummyUser3.publicId)
    dummyUser4Profile = Profile(userId=dummyUser4.publicId)
    dummyUser5Profile = Profile(userId=dummyUser5.publicId)

    db.session.add(dummyUser1)
    db.session.add(dummyUser2)
    db.session.add(dummyUser3)
    db.session.add(dummyUser4)
    db.session.add(dummyUser5)
    db.session.add(dummyUser1Profile)
    db.session.add(dummyUser2Profile)
    db.session.add(dummyUser3Profile)
    db.session.add(dummyUser4Profile)
    db.session.add(dummyUser5Profile)

    db.session.add(adminUser)
    db.session.add(adminRole)
    db.session.add(adminUserRole)
    db.session.add(stake)
    db.session.add(noMembership)
    db.session.add(adminUserProfile)
    db.session.add(adminUserMembership)
    db.session.commit()