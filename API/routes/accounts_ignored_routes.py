import re, uuid, random
import os, string
# Time checkers
from datetime import datetime, timedelta
import time

# Requests, Generate Password and Check Password
from flask import Blueprint, jsonify, request

# Models and database
from ..extensions import db
from ..models import Platform, User, SentCode, Account, Ignored

accounts_ignored_routes = Blueprint('accounts_ignored_routes', __name__)



def generateCode(length):
    stringLength=length
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for i in range(stringLength))



# ------------------- SEND LINKED ACCOUNT CODE ---------------------- #
@accounts_ignored_routes.route('/account/link/code', methods=['POST'])
def send_linked_account_code():
    data = request.get_json()
    try:
        platform = data["platform"]
        if Platform.query.filter_by(name=platform).first() == None:
            return jsonify({"message":"Platform does not exist!"})
        account = data["account"]
        username = data["username"]
        if User.query.filter_by(username=username).first() == None:
            return jsonify({"message":"Username does not exist!"})
        profileId = User.query.filter_by(username=username).first().publicId
        # ------- TODO ------- #
        # ACCEPT FRIENDSHIP OF MEMBER IF EXISTING
        # ------- TODO ------- #
        code = generateCode(6)
        if Account.query.filter_by(username=account, platform=platform).first() != None:
            return jsonify({"message":"Account already linked to a profile"})
        new_account = Account(username=account, platform=platform, profileId=profileId)
        Code = SentCode(username=account, code=code, valid_until=datetime.now() + timedelta(minutes=30))
        # ------- TODO ------- #
        # SEND MESSAGE ON PLATFORM WITH CODE
        # ------- TODO ------- #
        db.session.add(new_account)
        db.session.commit()
        db.session.add(Code)
        db.session.commit()
        return jsonify({"message":code})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- ADD LINKED ACCOUNT ---------------------- #
@accounts_ignored_routes.route('/account/link', methods=['POST'])
def add_linked_account():
    data = request.get_json()
    try:
        code = data["code"]
        account = data["account"]
        username = data["username"]
        platform = data["platform"]
        if Platform.query.filter_by(name=platform).first() == None:
            return jsonify({"message":"Platform does not exist"})
        sentCode = SentCode.query.filter_by(username=account, code=code).first()
        if sentCode == None:
            return jsonify({"message":"Code is incorrect or no codes have been sent"})
        if sentCode.valid_until < datetime.now():
            return jsonify({"message":"Code is invalid since {}".format(sentCode.valid_until)})
        user = User.query.filter_by(username=username).first()
        if user == None:
            return jsonify({"message":"User does not exist"})
        linked = Account.query.filter_by(username=account, profileId=user.publicId, platform=platform).first()
        if linked.verified == True:
            return jsonify({"message":"Account already linked"})
        linked.verified = True
        db.session.commit()
        return jsonify({"message":"Account linked successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- REMOVE LINKED ACCOUNT ---------------------- #
@accounts_ignored_routes.route('/account/link', methods=['DELETE'])
def remove_linked_account():
    data = request.get_json()
    try:
        username = data["username"]
        account = data["account"]
        platform = data["platform"]
        user = User.query.filter_by(username=username).first()
        if user == None:
            return jsonify({"message":"User does not exist"})
        linked = Account.query.filter_by(username=account, platform=platform, profileId=user.publicId).first()
        if linked == None:
            return jsonify({"message":"Linked account does not exist"})
        db.session.delete(linked)
        db.session.commit()
        return jsonify({"message":"Account removed successfully!"})
    except EXception as e:
        return jsonify({"message":str(e)})



# ------------------- GET ALL LINKED ACCOUNTS ---------------------- #
@accounts_ignored_routes.route('/accounts/link', methods=['GET'])
def get_linked_accounts():
    accounts = Account.query.all()

    out = []

    for account in accounts:
        account_data = account.__dict__
        del account_data["_sa_instance_state"]
        out.append(account_data)

    return jsonify(out)



# ------------------- GET LINKED ACCOUNTS BY NAME ---------------------- #
@accounts_ignored_routes.route('/accounts/link/name/<name>', methods=['GET'])
def get_linked_accounts_name(name):
    accounts = Account.query.filter_by(username=name).all()

    out = []

    for account in accounts:
        account_data = account.__dict__
        del account_data["_sa_instance_state"]
        out.append(account_data)

    return jsonify(out)



# ------------------- GET LINKED ACCOUNTS BY PLATFORM ---------------------- #
@accounts_ignored_routes.route('/accounts/link/platform/<platform>', methods=['GET'])
def get_linked_accounts_platform(platform):
    accounts = Account.query.filter_by(platform=platform).all()

    out = []

    for account in accounts:
        account_data = account.__dict__
        del account_data["_sa_instance_state"]
        out.append(account_data)

    return jsonify(out)



# ------------------- GET LINKED ACCOUNTS BY USERID ---------------------- #
@accounts_ignored_routes.route('/accounts/link/userid/<uid>', methods=['GET'])
def get_linked_accounts_userid(uid):
    accounts = Account.query.filter_by(profileId=uid).all()

    out = []

    for account in accounts:
        account_data = account.__dict__
        del account_data["_sa_instance_state"]
        out.append(account_data)

    return jsonify(out)



# ------------------- GET LINKED ACCOUNTS BY USERNAME ---------------------- #
@accounts_ignored_routes.route('/accounts/link/username/<username>', methods=['GET'])
def get_linked_accounts_username(username):
    user = User.query.filter_by(username=username).first()
    if user == None:
        return jsonify({"message":"User does not exist"})
    accounts = Account.query.filter_by(profileId=user.publicId).all()

    out = []

    for account in accounts:
        account_data = account.__dict__
        del account_data["_sa_instance_state"]
        out.append(account_data)

    return jsonify(out)



# ------------------- IGNORE USER ---------------------- #
@accounts_ignored_routes.route('/account/ignore', methods=['POST'])
def ignore_user():
    data = request.get_json()
    try:
        ignorer = data["username"]
        ignored = data["ignore"]
        ignorerUser = User.query.filter_by(username=ignorer).first()
        if ignorerUser == None:
            return jsonify({"message":"Ignorer username incorrect"})
        ignoredUser = User.query.filter_by(username=ignored).first()
        if ignoredUser == None:
            return jsonify({"message":"Ignored username incorrect"})
        if Ignored.query.filter_by(ignoredById=ignorerUser.publicId, ignoredId=ignoredUser.publicId).first() != None:
            return jsonify({"message":"User already ignored"})
        ignore = Ignored(ignoredById=ignorerUser.publicId, ignoredId=ignoredUser.publicId)
        db.session.add(ignore)
        db.session.commit()
        return jsonify({"message":"User ignored successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- UNIGNORE USER ---------------------- #
@accounts_ignored_routes.route('/account/ignore', methods=['DELETE'])
def unignore_user():
    data = request.get_json()
    try:
        ignorer = data["username"]
        ignored = data["ignore"]
        ignorerUser = User.query.filter_by(username=ignorer).first()
        if ignorerUser == None:
            return jsonify({"message":"Ignorer username incorrect"})
        ignoredUser = User.query.filter_by(username=ignored).first()
        if ignoredUser == None:
            return jsonify({"message":"Ignored username incorrect"})
        ignore = Ignored.query.filter_by(ignoredById=ignorerUser.publicId, ignoredId=ignoredUser.publicId).first()
        if ignore == None:
            return jsonify({"message":"User not ignored"})
        db.session.delete(ignore)
        db.session.commit()
        return jsonify({"message":"User unignored successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- GET ALL IGNORES ---------------------- #
@accounts_ignored_routes.route('/accounts/ignore', methods=['GET'])
def get_all_ignored():
    ignores = Ignored.query.all()

    out = []

    for ignore in ignores:
        ignore_data = ignore.__dict__
        del ignore_data["_sa_instance_state"]
        out.append(ignore_data)

    return jsonify(out)



# ------------------- GET IGNORES BY IGNORER ID ---------------------- #
@accounts_ignored_routes.route('/accounts/ignore/ignorer/id/<uid>', methods=['GET'])
def get_all_ignored_ignorerid(uid):
    ignores = Ignored.query.filter_by(ignoredById=uid).all()

    out = []

    for ignore in ignores:
        ignore_data = ignore.__dict__
        del ignore_data["_sa_instance_state"]
        out.append(ignore_data)

    return jsonify(out)



# ------------------- GET IGNORES BY IGNORED ID ---------------------- #
@accounts_ignored_routes.route('/accounts/ignore/ignored/id/<uid>', methods=['GET'])
def get_all_ignored_ignoredid(uid):
    ignores = Ignored.query.filter_by(ignoredId=uid).all()

    out = []

    for ignore in ignores:
        ignore_data = ignore.__dict__
        del ignore_data["_sa_instance_state"]
        out.append(ignore_data)

    return jsonify(out)



# ------------------- GET IGNORES BY IGNORER USERNAME ---------------------- #
@accounts_ignored_routes.route('/accounts/ignore/ignorer/username/<username>', methods=['GET'])
def get_all_ignored_ignorer_username(username):
    user = User.query.filter_by(username=username).first()
    if user == None:
        return jsonify({"message":"User does not exist"})
    ignores = Ignored.query.filter_by(ignoredById=user.publicId).all()

    out = []

    for ignore in ignores:
        ignore_data = ignore.__dict__
        del ignore_data["_sa_instance_state"]
        out.append(ignore_data)

    return jsonify(out)



# ------------------- GET IGNORES BY IGNORED USERNAME ---------------------- #
@accounts_ignored_routes.route('/accounts/ignore/ignored/username/<username>', methods=['GET'])
def get_all_ignored_ignored_username(username):
    user = User.query.filter_by(username=username).first()
    if user == None:
        return jsonify({"message":"User does not exist"})
    ignores = Ignored.query.filter_by(ignoredId=user.publicId).all()

    out = []

    for ignore in ignores:
        ignore_data = ignore.__dict__
        del ignore_data["_sa_instance_state"]
        out.append(ignore_data)

    return jsonify(out)