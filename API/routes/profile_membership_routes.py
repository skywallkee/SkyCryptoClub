import re, uuid, random
import os
# Time checkers
import time
from datetime import datetime, date, time, timedelta

# Requests, Generate Password and Check Password
from flask import Blueprint, jsonify, request

# Models and database
from ..extensions import db
from ..models import User, Membership, Profile, ProfileMembership, \
                    BannedProfile, BanDue, Currency, Wallet
    
profile_membership_routes = Blueprint('profile_membership_routes', __name__)



# ------------------- GET ALL PROFILES ---------------------- #
@profile_membership_routes.route('/profiles', methods=['GET'])
def get_all_profiles():
    profiles = Profile.query.all()

    out = []

    for profile in profiles:
        profile_data = profile.__dict__
        del profile_data["_sa_instance_state"]
        out.append(profile_data)

    return jsonify(out)



# ------------------- GET PROFILE BY USERNAME ---------------------- #
@profile_membership_routes.route('/profile/username/<name>', methods=['GET'])
def get_profile_username(name):
    user = User.query.filter_by(username=name).first()
    if user == None:
        return jsonify({"message":"Username doesn't exist"})

    profile = Profile.query.filter_by(userId=user.publicId).first()
    if profile == None:
        return jsonify({"message":"User doesn't have a profile"})
    
    
    profile_data = profile.__dict__
    del profile_data["_sa_instance_state"]

    return jsonify(profile_data)



# ------------------- GET PROFILE BY EMAIL ---------------------- #
@profile_membership_routes.route('/profile/email/<mail>', methods=['GET'])
def get_profile_email(mail):
    user = User.query.filter_by(email=mail).first()
    if user == None:
        return jsonify({"message":"Unclaimed E-Mail"})

    profile = Profile.query.filter_by(userId=user.publicId).first()
    if profile == None:
        return jsonify({"message":"User doesn't have a profile"})
    
    
    profile_data = profile.__dict__
    del profile_data["_sa_instance_state"]

    return jsonify(profile_data)



# ------------------- GET PROFILE BY PUBLIC ID ---------------------- #
@profile_membership_routes.route('/profile/id/<pid>', methods=['GET'])
def get_profile_id(pid):
    user = User.query.filter_by(publicId=pid).first()
    if user == None:
        return jsonify({"message":"ID is incorrect"})

    profile = Profile.query.filter_by(userId=user.publicId).first()
    if profile == None:
        return jsonify({"message":"User doesn't have a profile"})
    
    
    profile_data = profile.__dict__
    del profile_data["_sa_instance_state"]

    return jsonify(profile_data)



# ------------------- GET PROFILES BY MIN-MAX XP ---------------------- #
@profile_membership_routes.route('/profiles/xp/<min>/<max>', methods=['GET'])
def get_profiles_min_max(min, max):
    try:
        min = float(min)
        max = float(max)
        if min > max and max != 0:
            return jsonify({"message": "Minimum must be smaller than maximum"})
        
        if max == 0:
            profiles = Profile.query.filter(Profile.xp>=min).all()
        else:
            profiles = Profile.query.filter(Profile.xp>=min).filter(Profile.xp<=max).all()

        if len(profiles) < 1:
            return jsonify({"message":"There is no profile in range"})

        out = []

        for profile in profiles:
            profile_data = profile.__dict__
            del profile_data["_sa_instance_state"]
            out.append(profile_data)

        return jsonify(out)
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- GET NOT BANNED PROFILES ---------------------- #
@profile_membership_routes.route('/profiles/notbanned/', methods=['GET'])
def get_not_banned_profiles():
    try:
        profiles = Profile.query.all()
        out = []
        for profile in profiles:
            bans = BannedProfile.query.filter_by(userId=profile.userId).all()
            banned = False
            for ban in bans:
                banDue = BanDue.query.filter_by(bId=ban.bId).first()
                if banDue.due > datetime.now():
                    banned = True
                    break
            if banned == False:
                profile_data = profile.__dict__
                del profile_data["_sa_instance_state"]
                username = User.query.filter_by(publicId=profile.userId).first().username
                profile_data["username"] = username
                out.append(profile_data)
        return jsonify(out)
                
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- GET PROFILES BY BAN ---------------------- #
@profile_membership_routes.route('/profiles/banned/', methods=['GET'])
def get_profiles_ban():
    try:
        profiles = Profile.query.all()
        out = []
        for profile in profiles:
            bans = BannedProfile.query.filter_by(userId=profile.userId).all()
            banned = False
            for ban in bans:
                banDue = BanDue.query.filter_by(bId=ban.bId).first()
                if banDue.due > datetime.now():
                    banned = True
                    break
            if banned == True:
                profile_data = profile.__dict__
                del profile_data["_sa_instance_state"]
                username = User.query.filter_by(publicId=profile.userId).first().username
                profile_data["username"] = username
                out.append(profile_data)
        return jsonify(out)
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- GET PROFILES BY MEMBERSHIP ---------------------- #
@profile_membership_routes.route('/profiles/membership/<name>', methods=['GET'])
def get_profiles_membership(name):
    try:
        membership = Membership.query.filter_by(name=name).first()
        if membership == None:
            return jsonify({"message":"Membership doesn't exist"})
        profileMemberships = ProfileMembership.query.filter_by(membership=name)
        out = []
        for profileMembership in profileMemberships:
            profile = Profile.query.filter_by(userId=profileMembership.userId).first()
            profile_data = profile.__dict__
            del profile_data["_sa_instance_state"]
            username = User.query.filter_by(publicId=profile.userId).first().username
            profile_data["username"] = username
            out.append(profile_data)
        if len(out) < 1:
            return jsonify({"message":"There is no user in the given membership"})
        return jsonify(out)
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- TOTAL BAN PROFILE ---------------------- #
@profile_membership_routes.route('/profile/ban/total', methods=['POST'])
def profile_total_ban():
    data = request.get_json()
    try:
        username = data["username"]
        until = datetime(data["year"], data["month"], data["day"])
        user = User.query.filter_by(username=username).first()
        if user == None:
            return jsonify({"message":"The given username doesn't exist"})
        banProfile = BannedProfile(userId=user.publicId, total_ban=True)
        db.session.add(banProfile)
        db.session.commit()
        banDue = BanDue(bId=banProfile.bId, due=until)
        db.session.add(banDue)
        db.session.commit()
        return jsonify({"message":"User banned successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- TOTAL UNBAN PROFILE ---------------------- #
@profile_membership_routes.route('/profile/unban/total', methods=['PUT'])
def profile_total_unban():
    data = request.get_json()
    try:
        username = data["username"]
        user = User.query.filter_by(username=username).first()
        if user == None:
            return jsonify({"message":"The given username doesn't exist"})
        bans = BannedProfile.query.filter_by(userId=user.publicId, total_ban=True).all()
        for ban in bans:
            banDue = BanDue.query.filter_by(bId=ban.bId).first()
            if banDue.due > datetime.now():
                banDue.due = datetime.now() - timedelta(weeks=100)
        db.session.commit()
        return jsonify({"message":"User unbanned successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- BORROW BAN PROFILE ---------------------- #
@profile_membership_routes.route('/profile/ban/borrow', methods=['POST'])
def profile_borrow_ban():
    data = request.get_json()
    try:
        username = data["username"]
        until = datetime(data["year"], data["month"], data["day"])
        user = User.query.filter_by(username=username).first()
        if user == None:
            return jsonify({"message":"The given username doesn't exist"})
        banProfile = BannedProfile(userId=user.publicId, borrow_ban=True)
        db.session.add(banProfile)
        db.session.commit()
        banDue = BanDue(bId=banProfile.bId, due=until)
        db.session.add(banDue)
        db.session.commit()
        return jsonify({"message":"User banned successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- BORROW UNBAN PROFILE ---------------------- #
@profile_membership_routes.route('/profile/unban/borrow', methods=['PUT'])
def profile_borrow_unban():
    data = request.get_json()
    try:
        username = data["username"]
        user = User.query.filter_by(username=username).first()
        if user == None:
            return jsonify({"message":"The given username doesn't exist"})
        bans = BannedProfile.query.filter_by(userId=user.publicId, borrow_ban=True).all()
        for ban in bans:
            banDue = BanDue.query.filter_by(bId=ban.bId).first()
            if banDue.due > datetime.now():
                banDue.due = datetime.now() - timedelta(weeks=100)
        db.session.commit()
        return jsonify({"message":"User unbanned successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- EXCHANGE BAN PROFILE ---------------------- #
@profile_membership_routes.route('/profile/ban/exchange', methods=['POST'])
def profile_exchange_ban():
    data = request.get_json()
    try:
        username = data["username"]
        until = datetime(data["year"], data["month"], data["day"])
        user = User.query.filter_by(username=username).first()
        if user == None:
            return jsonify({"message":"The given username doesn't exist"})
        banProfile = BannedProfile(userId=user.publicId, exchange_ban=True)
        db.session.add(banProfile)
        db.session.commit()
        banDue = BanDue(bId=banProfile.bId, due=until)
        db.session.add(banDue)
        db.session.commit()
        return jsonify({"message":"User banned successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- EXCHANGE UNBAN PROFILE ---------------------- #
@profile_membership_routes.route('/profile/unban/exchange', methods=['PUT'])
def profile_exchange_unban():
    data = request.get_json()
    try:
        username = data["username"]
        user = User.query.filter_by(username=username).first()
        if user == None:
            return jsonify({"message":"The given username doesn't exist"})
        bans = BannedProfile.query.filter_by(userId=user.publicId, exchange_ban=True).all()
        for ban in bans:
            banDue = BanDue.query.filter_by(bId=ban.bId).first()
            if banDue.due > datetime.now():
                banDue.due = datetime.now() - timedelta(weeks=100)
        db.session.commit()
        return jsonify({"message":"User unbanned successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- LEND BAN PROFILE ---------------------- #
@profile_membership_routes.route('/profile/ban/lend', methods=['POST'])
def profile_lend_ban():
    data = request.get_json()
    try:
        username = data["username"]
        until = datetime(data["year"], data["month"], data["day"])
        user = User.query.filter_by(username=username).first()
        if user == None:
            return jsonify({"message":"The given username doesn't exist"})
        banProfile = BannedProfile(userId=user.publicId, lend_ban=True)
        db.session.add(banProfile)
        db.session.commit()
        banDue = BanDue(bId=banProfile.bId, due=until)
        db.session.add(banDue)
        db.session.commit()
        return jsonify({"message":"User banned successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- LEND UNBAN PROFILE ---------------------- #
@profile_membership_routes.route('/profile/unban/lend', methods=['PUT'])
def profile_lend_unban():
    data = request.get_json()
    try:
        username = data["username"]
        user = User.query.filter_by(username=username).first()
        if user == None:
            return jsonify({"message":"The given username doesn't exist"})
        bans = BannedProfile.query.filter_by(userId=user.publicId, lend_ban=True).all()
        for ban in bans:
            banDue = BanDue.query.filter_by(bId=ban.bId).first()
            if banDue.due > datetime.now():
                banDue.due = datetime.now() - timedelta(weeks=100)
        db.session.commit()
        return jsonify({"message":"User unbanned successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- ADD XP TO PROFILE ---------------------- #
@profile_membership_routes.route('/profile/xp', methods=['PUT'])
def profile_add_xp():
    data = request.get_json()
    try:
        username = data["username"]
        xp = int(data["xp"])
        user = User.query.filter_by(username=username).first()
        if user == None:
            return jsonify({"message":"Username is incorrect"})
        profile = Profile.query.filter_by(userId=user.publicId).first()
        profile.xp = profile.xp + xp
        db.session.commit()
        return jsonify({"message":"XP added successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- REMOVE XP FROM PROFILE ---------------------- #
@profile_membership_routes.route('/profile/xp', methods=['DELETE'])
def profile_remove_xp():
    data = request.get_json()
    try:
        username = data["username"]
        xp = int(data["xp"])
        user = User.query.filter_by(username=username).first()
        if user == None:
            return jsonify({"message":"Username is incorrect"})
        profile = Profile.query.filter_by(userId=user.publicId).first()
        profile.xp = profile.xp - xp
        db.session.commit()
        return jsonify({"message":"XP subtracted successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- SET PROFILE PUBLIC STATS ---------------------- #
@profile_membership_routes.route('/profile/public/stats', methods=['PUT'])
def set_public_stats():
    data = request.get_json()
    try:
        username = data["username"]
        stats = data["public"]
        user = User.query.filter_by(username=username).first()
        if user == None:
            return jsonify({"message":"Username is incorrect"})
        profile = Profile.query.filter_by(userId=user.publicId).first()
        profile.public_stats = stats
        db.session.commit()
        return jsonify({"message":"Public stats set successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- SET PROFILE PUBLIC LEVEL ---------------------- #
@profile_membership_routes.route('/profile/public/level', methods=['PUT'])
def set_public_level():
    data = request.get_json()
    try:
        username = data["username"]
        level = data["public"]
        user = User.query.filter_by(username=username).first()
        if user == None:
            return jsonify({"message":"Username is incorrect"})
        profile = Profile.query.filter_by(userId=user.publicId).first()
        profile.public_level = level
        db.session.commit()
        return jsonify({"message":"Public level set successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- SET PROFILE PUBLIC XP ---------------------- #
@profile_membership_routes.route('/profile/public/xp', methods=['PUT'])
def set_public_xp():
    data = request.get_json()
    try:
        username = data["username"]
        xp = data["public"]
        user = User.query.filter_by(username=username).first()
        if user == None:
            return jsonify({"message":"Username is incorrect"})
        profile = Profile.query.filter_by(userId=user.publicId).first()
        profile.public_xp = xp
        db.session.commit()
        return jsonify({"message":"Public xp set successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- SET PROFILE PUBLIC NAME ---------------------- #
@profile_membership_routes.route('/profile/public/name', methods=['PUT'])
def set_public_name():
    data = request.get_json()
    try:
        username = data["username"]
        name = data["public"]
        user = User.query.filter_by(username=username).first()
        if user == None:
            return jsonify({"message":"Username is incorrect"})
        profile = Profile.query.filter_by(userId=user.publicId).first()
        profile.public_name = name
        db.session.commit()
        return jsonify({"message":"Public name set successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- CREATE CURRENCY WALLET FOR PROFILE ---------------------- #
@profile_membership_routes.route('/profile/wallet', methods=['POST'])
def create_currency_wallet():
    data = request.get_json()
    try:
        username = data["username"]
        currency = data["currency"]
        if "amount" in data:
            amount = float(data["amount"])
        else:
            amount = 0.0

        user = User.query.filter_by(username=username).first()
        if user == None:
            return jsonify({"message":"Username is incorrect"})
        currency = Currency.query.filter_by(name=currency).first()
        if currency == None:
            return jsonify({"message":"Currency is inexistent"})

        wallet = Wallet(userId=user.publicId, currency=currency.name, amount=amount)
        db.session.add(wallet)
        db.session.commit()
        return jsonify({"message":"Wallet created successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- GET CURRENCY WALLET FOR PROFILE ---------------------- #
@profile_membership_routes.route('/profile/<username>/wallet/<currency>', methods=['GET'])
def get_currency_wallet(username, currency):
    try:

        user = User.query.filter_by(username=username).first()
        if user == None:
            return jsonify({"message":"Username is incorrect"})
        currency = Currency.query.filter_by(name=currency).first()
        if currency == None:
            return jsonify({"message":"Currency is inexistent"})

        wallet = Wallet.query.filter_by(userId=user.publicId, currency=currency.name).first()
        if wallet == None:
            return jsonify({"message":"User doesn't have a wallet in given currency"})

        wallet = wallet.__dict__
        del wallet["_sa_instance_state"]
        return jsonify(wallet)
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- GET ALL WALLETS OF PROFILE ---------------------- #
@profile_membership_routes.route('/profile/<username>/wallets', methods=['GET'])
def get_currency_wallets(username):
    try:
        user = User.query.filter_by(username=username).first()
        if user == None:
            return jsonify({"message":"Username is incorrect"})

        wallets = Wallet.query.filter_by(userId=user.publicId).all()
        if len(wallets) < 1:
            return jsonify({"message":"User doesn't have any wallet"})

        out = []
        for wallet in wallets:
            wallet = wallet.__dict__
            del wallet["_sa_instance_state"]
            out.append(wallet)
        return jsonify(out)
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- ADD AMOUNT TO WALLET CURRENCY ---------------------- #
@profile_membership_routes.route('/profile/wallet', methods=['PUT'])
def add_amount_to_wallet():
    data = request.get_json()
    try:
        username = data["username"]
        user = User.query.filter_by(username=username).first()
        if user == None:
            return jsonify({"message":"Username is incorrect"})
        amount = float(data["amount"])
        currency = data["currency"]       
        currency = Currency.query.filter_by(name=currency).first()
        if currency == None:
            return jsonify({"message":"Currency is inexistent"})

        wallet = Wallet.query.filter_by(userId=user.publicId).first()
        if wallet == None:
            wallet = Wallet(userId=user.publicId, currency=currency.name, amount=amount)
            db.session.add(wallet)
        wallet.amount = wallet.amount + amount
        db.session.commit() 
        return jsonify({"message":"Amount added successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- REMOVE AMOUNT FROM WALLET CURRENCY ---------------------- #
@profile_membership_routes.route('/profile/wallet', methods=['DELETE'])
def remove_amount_to_wallet():
    data = request.get_json()
    try:
        username = data["username"]
        user = User.query.filter_by(username=username).first()
        if user == None:
            return jsonify({"message":"Username is incorrect"})
        amount = float(data["amount"])
        currency = data["currency"]       
        currency = Currency.query.filter_by(name=currency).first()
        if currency == None:
            return jsonify({"message":"Currency is inexistent"})

        wallet = Wallet.query.filter_by(userId=user.publicId).first()
        if wallet == None:
            return jsonify({"message":"User doesn't have a wallet with given currency"})
        wallet.amount = wallet.amount - amount
        db.session.commit() 
        return jsonify({"message":"Amount subtracted successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- WITHDRAW ---------------------- #
@profile_membership_routes.route('/profile/wallet/withdraw', methods=['DELETE'])
def withdraw_from_wallet():
    # ------------- TODO ------------- #
    return jsonify({"message":"Currently unavailable"})



# ------------------- CREATE MEMBERSHIP ---------------------- #
@profile_membership_routes.route('/membership', methods=['POST'])
def create_membership():
    data = request.get_json()
    try:
        name = data["name"]
        color = data["color"]
        price = float(data["price"])
        can_exchange = True if data["can_exchange"] == "True" else False
        can_borrow = True if data["can_borrow"] == "True" else False
        can_lend = True if data["can_lend"] == "True" else False
        exchange_small_fee = data["exchange_small_fee"]
        exchange_large_fee = data["exchange_large_fee"]
        exchange_limit = data["exchange_limit"]
        borrow_base_fee = data["borrow_base_fee"]
        borrow_daily_fee = data["borrow_daily_fee"]
        borrow_grace_fee = data["borrow_grace_fee"]
        minimum_interest = data["minimum_interest"]
        max_borrow_days = data["max_borrow_days"]
        max_grace_days = data["max_grace_days"]
        grace_penalty = data["grace_penalty"]
        max_borrow_amount = data["max_borrow_amount"]
        lend_first_fee = data["lend_first_fee"]
        lend_daily_fee = data["lend_daily_fee"]

        membership = Membership(name=name, color=color, \
        price=price, can_exchange=can_exchange, can_borrow=can_borrow, \
        can_lend=can_lend, exchange_small_fee=exchange_small_fee, \
        exchange_large_fee=exchange_large_fee, exchange_limit=exchange_limit, \
        borrow_base_fee=borrow_base_fee, borrow_daily_fee=borrow_daily_fee, \
        borrow_grace_fee=borrow_grace_fee, minimum_interest=minimum_interest, \
        max_borrow_days=max_borrow_days, max_grace_days=max_grace_days, \
        grace_penalty=grace_penalty, max_borrow_amount=max_borrow_amount, \
        lend_first_fee=lend_first_fee, lend_daily_fee=lend_daily_fee)

        db.session.add(membership)
        db.session.commit()
        
        return jsonify({"message":"Membership created successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- EDIT MEMBERSHIP ---------------------- #
@profile_membership_routes.route('/membership', methods=['PUT'])
def edit_membership():
    data = request.get_json()
    try:
        name = data["name"]
        membership = Membership.query.filter_by(name=name).first()
        if membership == None:
            return jsonify({"message":"Membership doesn't exist"})
        membership.name = data["new_name"] if "new_name" in data else membership.name
        membership.color = data["color"] if "color" in data else membership.color
        membership.price = data["price"] if "price" in data else membership.price
        if "can_exchange" in data:
            can_exchange = True if data["can_exchange"] == "True" else False
        else:
            can_exchange = membership.can_exchange
        membership.can_exchange = can_exchange
        if "can_borrow" in data:
            can_borrow = True if data["can_borrow"] == "True" else False
        else:
            can_borrow = membership.can_borrow
        membership.can_borrow = can_borrow
        if "can_lend" in data:
            can_lend = True if data["can_lend"] == "True" else False
        else:
            can_lend = membership.can_lend
        membership.can_lend = can_lend
        membership.exchange_small_fee = data["exchange_small_fee"] if "exchange_small_fee" in data else membership.exchange_small_fee
        membership.exchange_large_fee = data["exchange_large_fee"] if "exchange_large_fee" in data else membership.exchange_large_fee
        membership.exchange_limit = data["exchange_limit"] if "exchange_limit" in data else membership.exchange_limit
        membership.borrow_base_fee = data["borrow_base_fee"] if "borrow_base_fee" in data else membership.borrow_base_fee
        membership.borrow_daily_fee = data["borrow_daily_fee"] if "borrow_daily_fee" in data else membership.borrow_daily_fee
        membership.borrow_grace_fee = data["borrow_grace_fee"] if "borrow_grace_fee" in data else membership.borrow_grace_fee
        membership.minimum_interest = data["minimum_interest"] if "minimum_interest" in data else membership.minimum_interest
        membership.max_borrow_days = data["max_borrow_days"] if "max_borrow_days" in data else membership.max_borrow_days
        membership.max_grace_days = data["max_grace_days"] if "max_grace_days" in data else membership.max_grace_days
        membership.grace_penalty = data["grace_penalty"] if "grace_penalty" in data else membership.grace_penalty
        membership.max_borrow_amount = data["max_borrow_amount"] if "max_borrow_amount" in data else membership.max_borrow_amount
        membership.lend_first_fee = data["lend_first_fee"] if "lend_first_fee" in data else membership.lend_first_fee
        membership.lend_daily_fee = data["lend_daily_fee"] if "lend_daily_fee" in data else membership.lend_daily_fee
        db.session.commit()
        
        return jsonify({"message":"Membership edited successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- DELETE MEMBERSHIP ---------------------- #
@profile_membership_routes.route('/membership', methods=['DELETE'])
def delete_membership():
    data = request.get_json()
    try:
        name = data["name"]
        membership = Membership.query.filter_by(name=name).first()
        if membership == None:
            return jsonify({"message":"Membership doesn't exist"})
        profileMemberships = ProfileMembership.query.filter_by(membership=name).all()
        for profileMembership in profileMemberships:
            profileMembership.membership = Membership.query.filter(Membership.name!=name).first().name
        db.session.delete(membership)
        db.session.commit()
        
        return jsonify({"message":"Membership deleted successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- SET PROFILE TO MEMBERSHIP ---------------------- #
@profile_membership_routes.route('/profile/membership', methods=['POST'])
def set_profile_membership():
    data = request.get_json()
    try:
        username = data["username"]
        name = data["membership"]
        valid = datetime(data["valid_year"], data["valid_month"], data["valid_day"])
        membership = Membership.query.filter_by(name=name).first()
        if membership == None:
            return jsonify({"message":"Membership doesn't exist"})
        user = User.query.filter_by(username=username).first()
        if username == None:
            return jsonify({"message":"User doesn't exist"})
        profileMembership = ProfileMembership.query.filter_by(userId=user.publicId, membership=name).first()
        if profileMembership != None:
            return jsonify({"message":"User already in this membership"})
        profileMembership = ProfileMembership.query.filter_by(userId=user.publicId).first()
        if profileMembership != None:
            profileMembership.membership = name
            profileMembership.valid_until = valid
        else:
            membership = ProfileMembership(userId=user.publicId, membership=name, valid_until=valid)
            db.session.add(membership)
        db.session.commit()
        return jsonify({"message":"User added successfully in membership!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- EXTEND PROFILE MEMBERSHIP ---------------------- #
@profile_membership_routes.route('/profile/membership', methods=['PUT'])
def extend_profile_membership():
    data = request.get_json()
    try:
        username = data["username"]
        days = int(data["days"])
        user = User.query.filter_by(username=username).first()
        if username == None:
            return jsonify({"message":"User doesn't exist"})
        profileMembership = ProfileMembership.query.filter_by(userId=user.publicId).first()
        profileMembership.valid_until += timedelta(days=days)
        db.session.commit()
        return jsonify({"message":"Extension of membership successful!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- GET ALL PROFILE MEMBERSHIPS ---------------------- #
@profile_membership_routes.route('/profile/memberships', methods=['GET'])
def get_profile_memberships():
    try:
        memberships = ProfileMembership.query.all()

        out = []

        for membership in memberships:
            membership_data = membership.__dict__
            del membership_data["_sa_instance_state"]
            out.append(membership_data)

        return jsonify(out)
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- GET ALL MEMBERSHIPS ---------------------- #
@profile_membership_routes.route('/memberships', methods=['GET'])
def get_memberships():
    try:
        memberships = Membership.query.all()

        out = []

        for membership in memberships:
            membership_data = membership.__dict__
            del membership_data["_sa_instance_state"]
            out.append(membership_data)

        return jsonify(out)
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- GET MEMBERSHIP BY NAME ---------------------- #
@profile_membership_routes.route('/membership/<name>', methods=['GET'])
def get_membership_name(name):
    try:
        membership = Membership.query.filter_by(name=name).first()
        if membership == None:
            return jsonify({"message":"Membership doesn't exist"})

        membership_data = membership.__dict__
        del membership_data["_sa_instance_state"]

        return jsonify(membership_data)
    except Exception as e:
        return jsonify({"message":str(e)})