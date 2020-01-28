import click, uuid
from werkzeug.security import generate_password_hash
from flask.cli import with_appcontext

from .extensions import db
from .models import User, Platform, Account, Membership, Role,\
    UserRole, Profile, Ignored, ProfileMembership, Currency, \
    BorrowStatus, Borrow, ExchangeStatus, Exchange, FAQCategory, FAQ

@click.command(name='create_tables')
@with_appcontext
def create_tables():
    db.create_all()
    # Defaults
    adminUser = User(publicId=str(uuid.uuid4()), username="Admin", password=generate_password_hash("Admin", "sha256"), email="support@skycrypto.club")
    userRole = Role(name="User", color="grey", defaultR=True, admin_panel=False, admin_statistics=False,\
        edit_memberships=False, create_memberships=False, delete_memberships=False, add_platform=False,\
        edit_platform=False, delete_platform=False, ban_user=False, edit_xp=False, edit_user_membership=False,\
        add_currency=False, edit_currency=False, delete_currency=False, add_borrow_status=False,\
        edit_borrow_status=False, remove_borrow_status=False, edit_borrow=False, add_exchange_status=False,\
        edit_exchange_status=False, remove_exchange_status=False, edit_exchange=False, add_faq_category=False,\
        edit_faq_category=False, remove_faq_category=False, add_account=False, edit_account=False, assign_role=False,\
        moderation_panel=False, ban_exchange=False, ban_borrow=False, ban_lend=False, edit_name=False, add_ignored=False,\
        remove_ignored=False, close_exchange=False, close_borrow=False, support_panel=False, view_tickets=False,\
        respond_tickets=False, close_tickets=False, reopen_tickets=False, add_faq=False, edit_faq=False, remove_faq=False,\
        view_user_borrows=False, view_user_lendings=False, view_user_profile=False, view_user_exchanges=False,\
        view_exchange=False, view_borrow=False, view_user_balance=False, delete_account=False)
    adminRole = Role(name="Admin", color="red", defaultR=False, admin_panel=True, admin_statistics=True,\
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
    noMembership = Membership(name="None", color="gray", price=0, can_exchange=True, can_borrow=False, can_lend=False,\
        exchange_small_fee=0.07, exchange_large_fee=0.05, exchange_limit=0.6, borrow_base_fee=0.02, borrow_daily_fee=0.01,\
        borrow_grace_fee=0.01, minimum_interest=0.1, max_borrow_days=7, max_grace_days=7, grace_penalty=0.05,\
        max_borrow_amount=0.6, lend_first_fee=1, lend_daily_fee=1, defaultM=True)
    adminUserProfile = Profile(userId=adminUser.publicId)
    adminUserMembership = ProfileMembership(userId=adminUserProfile.userId, membership=noMembership.name)
    db.session.add(adminUser)
    db.session.add(userRole)
    db.session.add(adminRole)
    db.session.add(adminUserRole)
    db.session.add(stake)
    db.session.add(noMembership)
    db.session.add(adminUserProfile)
    db.session.add(adminUserMembership)
    db.session.commit()