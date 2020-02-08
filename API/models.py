from .extensions import db
from datetime import datetime

class User(db.Model):
    # User login table, unseen by users
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    publicId = db.Column(db.String(80), unique=True)
    username = db.Column(db.String(35), unique=True)
    password = db.Column(db.String(80))
    email = db.Column(db.String(80), unique=True)
    otp_token = db.Column(db.String(80), default="")
    last_pass_reset = db.Column(db.DateTime, default=datetime.now())

class Role(db.Model):
    # Table with available user roles and permissions
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(35), nullable=False)
    color = db.Column(db.String(35), nullable=False)
    defaultR = db.Column(db.Boolean, default=False)

    # Admin Permissions
    admin_panel = db.Column(db.Boolean, default=False)
    admin_statistics = db.Column(db.Boolean, default=False)
    edit_memberships = db.Column(db.Boolean, default=False)
    create_memberships = db.Column(db.Boolean, default=False)
    delete_memberships = db.Column(db.Boolean, default=False)
    add_platform = db.Column(db.Boolean, default=False)
    edit_platform = db.Column(db.Boolean, default=False)
    delete_platform = db.Column(db.Boolean, default=False)
    ban_user = db.Column(db.Boolean, default=False)
    edit_xp = db.Column(db.Boolean, default=False)
    edit_user_membership = db.Column(db.Boolean, default=False)
    add_currency = db.Column(db.Boolean, default=False)
    edit_currency = db.Column(db.Boolean, default=False)
    delete_currency = db.Column(db.Boolean, default=False)
    add_borrow_status = db.Column(db.Boolean, default=False)
    edit_borrow_status = db.Column(db.Boolean, default=False)
    remove_borrow_status = db.Column(db.Boolean, default=False)
    edit_borrow = db.Column(db.Boolean, default=False)
    add_exchange_status = db.Column(db.Boolean, default=False)
    edit_exchange_status = db.Column(db.Boolean, default=False)
    remove_exchange_status = db.Column(db.Boolean, default=False)
    edit_exchange = db.Column(db.Boolean, default=False)
    add_faq_category = db.Column(db.Boolean, default=False)
    edit_faq_category = db.Column(db.Boolean, default=False)
    remove_faq_category = db.Column(db.Boolean, default=False)
    add_account = db.Column(db.Boolean, default=False)
    edit_account = db.Column(db.Boolean, default=False)
    assign_role = db.Column(db.Boolean, default=False)

    # Moderator Permissions
    moderation_panel = db.Column(db.Boolean, default=False)
    ban_exchange = db.Column(db.Boolean, default=False)
    ban_borrow = db.Column(db.Boolean, default=False)
    ban_lend = db.Column(db.Boolean, default=False)
    edit_name = db.Column(db.Boolean, default=False)
    add_ignored = db.Column(db.Boolean, default=False)
    remove_ignored = db.Column(db.Boolean, default=False)
    close_exchange = db.Column(db.Boolean, default=False)
    close_borrow = db.Column(db.Boolean, default=False)

    # Support Permissions
    support_panel = db.Column(db.Boolean, default=False)
    view_tickets = db.Column(db.Boolean, default=False)
    respond_tickets = db.Column(db.Boolean, default=False)
    close_tickets = db.Column(db.Boolean, default=False)
    reopen_tickets = db.Column(db.Boolean, default=False)
    add_faq = db.Column(db.Boolean, default=False)
    edit_faq = db.Column(db.Boolean, default=False)
    remove_faq = db.Column(db.Boolean, default=False)
    view_user_borrows = db.Column(db.Boolean, default=False)
    view_user_lendings = db.Column(db.Boolean, default=False)
    view_user_profile = db.Column(db.Boolean, default=False)
    view_user_exchanges = db.Column(db.Boolean, default=False)
    view_exchange = db.Column(db.Boolean, default=False)
    view_borrow = db.Column(db.Boolean, default=False)
    view_user_balance = db.Column(db.Boolean, default=False)
    delete_account = db.Column(db.Boolean, default=False)

class UserRole(db.Model):
    # Table with each user's roles
    __tablename__ = 'userrole'
    userId = db.Column(db.String(80), db.ForeignKey('user.publicId'), primary_key=True)
    role = db.Column(db.String(35), db.ForeignKey('role.name'), primary_key=True)

class Platform(db.Model):
    __tablename__ = 'platform'
    # Partnered platforms available on SCC
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(35), nullable=False, unique=True)

class Membership(db.Model):
    __tablename__ = 'membership'
    # Table with all available memberships
    name = db.Column(db.String(25), primary_key=True)
    defaultM = db.Column(db.Boolean, default=False)
    color = db.Column(db.String(35))
    price = db.Column(db.Float(precision=10)) # BTC Price
    can_exchange = db.Column(db.Boolean)
    can_borrow = db.Column(db.Boolean)
    can_lend = db.Column(db.Boolean)
    exchange_small_fee = db.Column(db.Float)
    exchange_large_fee = db.Column(db.Float)
    exchange_limit = db.Column(db.Float)
    borrow_base_fee = db.Column(db.Float)
    borrow_daily_fee = db.Column(db.Float)
    borrow_grace_fee = db.Column(db.Float)
    minimum_interest = db.Column(db.Float)
    max_borrow_days = db.Column(db.Integer)
    max_grace_days = db.Column(db.Integer)
    grace_penalty = db.Column(db.Float)
    max_borrow_amount = db.Column(db.Float)
    lend_first_fee = db.Column(db.Float)
    lend_daily_fee = db.Column(db.Float)

class Profile(db.Model):
    __tablename__ = 'profile'
    # Table for user profile available publicly
    userId = db.Column(db.String(80), db.ForeignKey('user.publicId'), primary_key=True)
    xp = db.Column(db.Float, default=0.0)
    public_stats = db.Column(db.Boolean, default=True)
    public_level = db.Column(db.Boolean, default=True)
    public_xp = db.Column(db.Boolean, default=True)
    public_name = db.Column(db.Boolean, default=True)
    has_tfa = db.Column(db.Boolean, default=False)

class BannedProfile(db.Model):
    __tablename__ = 'bannedprofile'
    # Table of users that have any kind of ban
    bId = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String(80), db.ForeignKey('profile.userId'))
    total_ban = db.Column(db.Boolean, default=False)
    exchange_ban = db.Column(db.Boolean, default=False)
    borrow_ban = db.Column(db.Boolean, default=False)
    lend_ban = db.Column(db.Boolean, default=False)

class BanDue(db.Model):
    __tablename__ = 'bandue'
    bId = db.Column(db.Integer, db.ForeignKey('bannedprofile.bId'), primary_key=True)
    due = db.Column(db.DateTime)

class Wallet(db.Model):
    __tablename__ = 'wallet'
    # Table for user's balances
    userId = db.Column(db.String(80), db.ForeignKey('profile.userId'), primary_key=True)
    currency = db.Column(db.String(20), db.ForeignKey('currency.name'), primary_key=True)
    amount = db.Column(db.Float(precision=10), default=0.0)

class Account(db.Model):
    __tablename__ = 'account'
    # Linked accounts from partnered platforms
    username = db.Column(db.String(35), primary_key=True)
    platform = db.Column(db.String(35), db.ForeignKey('platform.name'), primary_key=True)
    profileId = db.Column(db.String(80), db.ForeignKey('profile.userId'))
    verified = db.Column(db.Boolean, default=False)

class SentCode(db.Model):
    __tablename__ = 'sentcodes'
    # Sent codes for accounts to be verified
    sentId = db.Column(db.Integer, primary_key=True)
    profileId = db.Column(db.String(80), db.ForeignKey('profile.userId'))
    username = db.Column(db.String(35), db.ForeignKey('account.username'))
    code = db.Column(db.String(64))
    valid_until = db.Column(db.DateTime)

class Ignored(db.Model):
    __tablename__ = 'ignored'
    # Table of users that have been ignored
    ignoredById = db.Column(db.String(80), db.ForeignKey('profile.userId'), primary_key=True)
    ignoredId = db.Column(db.String(80), db.ForeignKey('profile.userId'), primary_key=True)

class ProfileMembership(db.Model):
    __tablename__ = 'profilemembership'
    # Table with memberships of all users
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String(80), db.ForeignKey('profile.userId'), unique=True)
    membership = db.Column(db.String(25), db.ForeignKey('membership.name'))
    valid_until = db.Column(db.DateTime)

class Currency(db.Model):
    __tablename__ = 'currency'
    # Table that displays all the currencies available on 
    # our website paired with the platform they can be used on
    name = db.Column(db.String(20), primary_key=True)
    large_name = db.Column(db.String(20), nullable=False)
    platform = db.Column(db.String(35), db.ForeignKey('platform.name'), primary_key=True)

class BorrowStatus(db.Model):
    __tablename__ = 'borrowstatus'
    # Table with borrow statuses
    status = db.Column(db.String(80), primary_key=True)

class Borrow(db.Model):
    __tablename__ = 'borrow'
    # Table with all borrow requests
    id = db.Column(db.Integer, primary_key=True)
    ref_id = db.Column(db.String(80), unique=True)
    currency = db.Column(db.String(20), db.ForeignKey('currency.name'))
    amount = db.Column(db.Float(precision=10))
    paid = db.Column(db.Float(precision=10), default=0)
    by_id = db.Column(db.String(80), db.ForeignKey('profile.userId'))
    through_id = db.Column(db.String(80), db.ForeignKey('profile.userId'))
    interest = db.Column(db.Float)
    status = db.Column(db.String(80), db.ForeignKey('borrowstatus.status'))
    return_date = db.Column(db.DateTime)
    grace_date = db.Column(db.DateTime)
    created_date = db.Column(db.DateTime)

class ExchangeStatus(db.Model):
    __tablename__ = 'exchangestatus'
    # Table with exchange statuses
    status = db.Column(db.String(80), primary_key=True)

class Exchange(db.Model):
    __tablename__ = 'exchange'
    # Table with all exchange requests
    id = db.Column(db.Integer, primary_key=True)
    ref_id = db.Column(db.String(80), unique=True)
    from_currency = db.Column(db.String(20), db.ForeignKey('currency.name'))
    from_amount = db.Column(db.Float(precision=10))
    to_currency = db.Column(db.String(20), db.ForeignKey('currency.name'))
    to_amount = db.Column(db.Float(precision=10))
    by_id = db.Column(db.String(80), db.ForeignKey('profile.userId'))
    through_id = db.Column(db.String(80), db.ForeignKey('profile.userId'))
    status = db.Column(db.String(80), db.ForeignKey('exchangestatus.status'))
    created_date = db.Column(db.DateTime)

class FAQCategory(db.Model):
    __tablename__ = 'faqcategory'
    # Table with FAQ categories
    name = db.Column(db.String(80), primary_key=True)

class FAQ(db.Model):
    __tablename__ = 'faq'
    # Table with Frequent Asked Questions
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(80), db.ForeignKey('faqcategory.name'), unique=True)
    question = db.Column(db.String(256), unique=True)
    answer = db.Column(db.String(256))