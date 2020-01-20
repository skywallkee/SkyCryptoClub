from .extensions import db

class User(db.Model):
    # User login table, unseen by users
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    publicId = db.Column(db.String(80), unique=True)
    username = db.Column(db.String(35), unique=True)
    password = db.Column(db.String(80))
    email = db.Column(db.String(80), unique=True)
    otp_token = db.Column(db.String(80), default="")

class Role(db.Model):
    # Table with available user roles and permissions
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(35))
    color = db.Column(db.String(35))
    defaultR = db.Column(db.Boolean)
    # Admin Permissions
    admin_panel = db.Column(db.Boolean)
    admin_statistics = db.Column(db.Boolean)
    edit_memberships = db.Column(db.Boolean)
    create_memberships = db.Column(db.Boolean)
    delete_memberships = db.Column(db.Boolean)
    add_platform = db.Column(db.Boolean)
    edit_platform = db.Column(db.Boolean)
    delete_platform = db.Column(db.Boolean)
    ban_user = db.Column(db.Boolean)
    edit_xp = db.Column(db.Boolean)
    edit_user_membership = db.Column(db.Boolean)
    add_currency = db.Column(db.Boolean)
    edit_currency = db.Column(db.Boolean)
    delete_currency = db.Column(db.Boolean)
    add_borrow_status = db.Column(db.Boolean)
    edit_borrow_status = db.Column(db.Boolean)
    remove_borrow_status = db.Column(db.Boolean)
    edit_borrow = db.Column(db.Boolean)
    add_exchange_status = db.Column(db.Boolean)
    edit_exchange_status = db.Column(db.Boolean)
    remove_exchange_status = db.Column(db.Boolean)
    edit_exchange = db.Column(db.Boolean)
    add_faq_category = db.Column(db.Boolean)
    edit_faq_category = db.Column(db.Boolean)
    remove_faq_category = db.Column(db.Boolean)
    add_account = db.Column(db.Boolean)
    edit_account = db.Column(db.Boolean)
    assign_role = db.Column(db.Boolean)

    # Moderator Permissions
    moderation_panel = db.Column(db.Boolean)
    ban_exchange = db.Column(db.Boolean)
    ban_borrow = db.Column(db.Boolean)
    ban_lend = db.Column(db.Boolean)
    edit_name = db.Column(db.Boolean)
    add_ignored = db.Column(db.Boolean)
    remove_ignored = db.Column(db.Boolean)
    close_exchange = db.Column(db.Boolean)
    close_borrow = db.Column(db.Boolean)

    # Support Permissions
    support_panel = db.Column(db.Boolean)
    view_tickets = db.Column(db.Boolean)
    respond_tickets = db.Column(db.Boolean)
    close_tickets = db.Column(db.Boolean)
    reopen_tickets = db.Column(db.Boolean)
    add_faq = db.Column(db.Boolean)
    edit_faq = db.Column(db.Boolean)
    remove_faq = db.Column(db.Boolean)
    view_user_borrows = db.Column(db.Boolean)
    view_user_lendings = db.Column(db.Boolean)
    view_user_profile = db.Column(db.Boolean)
    view_user_exchanges = db.Column(db.Boolean)
    view_exchange = db.Column(db.Boolean)
    view_borrow = db.Column(db.Boolean)
    view_user_balance = db.Column(db.Boolean)
    delete_account = db.Column(db.Boolean)

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
    defaultM = db.Column(db.Boolean)
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
    banned = db.Column(db.Boolean, default=False)
    exchange_ban_due = db.Column(db.DateTime)
    borrow_ban_due = db.Column(db.DateTime)
    lend_ban_due = db.Column(db.DateTime)
    xp = db.Column(db.Float, default=0.0)
    public_stats = db.Column(db.Boolean, default=True)
    public_level = db.Column(db.Boolean, default=True)
    public_xp = db.Column(db.Boolean, default=True)
    public_name = db.Column(db.Boolean, default=True)
    has_tfa = db.Column(db.Boolean, default=False)

class Account(db.Model):
    __tablename__ = 'account'
    # Linked accounts from partnered platforms
    username = db.Column(db.String(35), primary_key=True)
    platform = db.Column(db.String(35), db.ForeignKey('platform.name'), primary_key=True)
    profileId = db.Column(db.String(80), db.ForeignKey('profile.userId'))

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
    paid_per_day = db.Column(db.Float, default=0)

class Currency(db.Model):
    __tablename__ = 'currency'
    # Table that displays all the currencies available on 
    # our website paired with the platform they can be used on
    name = db.Column(db.String(20), primary_key=True)
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