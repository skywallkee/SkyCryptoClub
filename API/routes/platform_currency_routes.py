import re, uuid, random
import os
# Time checkers
from datetime import datetime
import time

# Requests, Generate Password and Check Password
from flask import Blueprint, jsonify, request

# Models and database
from ..extensions import db
from ..models import Platform, Currency
    
platform_currency_routes = Blueprint('platform_currency_routes', __name__)

# ------------------- CREATE NEW PLATFORM ---------------------- #
@platform_currency_routes.route('/platform', methods=['POST'])
def create_platform():
    data = request.get_json()
    try:
        platform = Platform.query.filter_by(name=data["name"]).all()
        if len(platform) > 0:
            return jsonify({"message":"The given platform already exists"})

        platform = Platform(**data)

        db.session.add(platform)
        db.session.commit()
        return jsonify({"message":"Platform created successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- EDIT PLATFORM ---------------------- #
@platform_currency_routes.route('/platform', methods=['PUT'])
def edit_platform():
    data = request.get_json()
    try:
        name = data["platform"]
        del data["platform"]
        platform = Platform.query.filter_by(name=name).all()
        if len(platform) < 1:
            return jsonify({"message":"The given platform doesn't exist"})

        platform = platform[0]
        for key, value in data.items():
            setattr(platform, key, value)

        db.session.commit()
        return jsonify({"message":"Platform updated successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- DELETE PLATFORM ---------------------- #
@platform_currency_routes.route('/platform', methods=['DELETE'])
def delete_platform():
    data = request.get_json()
    try:
        name = data["platform"]
        platform = Platform.query.filter_by(name=name).all()
        if len(platform) < 1:
            return jsonify({"message":"The given platform doesn't exist"})
        platform = platform[0]
        db.session.delete(platform)
        db.session.commit()
        return jsonify({"message":"Platform deleted successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- GET PLATFORM BY NAME ---------------------- #
@platform_currency_routes.route('/platform/name/<name>', methods=['GET'])
def get_platform_by_name(name):
    platform = Platform.query.filter_by(name=name).first()
    if platform == None:
        return jsonify({"message":"Platform doesn't exist"})
    platform = platform.__dict__
    del platform["_sa_instance_state"]
    return jsonify(platform)



# ------------------- GET PLATFORM BY ID ---------------------- #
@platform_currency_routes.route('/platform/id/<pid>', methods=['GET'])
def get_platform_by_id(pid):
    platform = Platform.query.filter_by(id=pid).first()
    if platform == None:
        return jsonify({"message":"Platform doesn't exist"})
    platform = platform.__dict__
    del platform["_sa_instance_state"]
    return jsonify(platform)



# ------------------- GET ALL PLATFORMS ---------------------- #
@platform_currency_routes.route('/platforms', methods=['GET'])
def get_all_platforms():
    platformlist = Platform.query.all()
    platforms = []

    for platform in platformlist:
        platform = platform.__dict__
        del platform["_sa_instance_state"]
        platforms.append(platform)
    return jsonify(platforms)



# ------------------- CREATE NEW CURRENCY ---------------------- #
@platform_currency_routes.route('/currency', methods=['POST'])
def create_currency():
    data = request.get_json()
    try:
        currencies_to_add = []
        data["large_name"]
        # ------------------- CREATE NEW CURRENCY TO ONE PLATFORM ---------------------- #
        if "platform" in data:
            platform = Platform.query.filter_by(name=data["platform"]).all()
            if len(platform) < 1:
                return jsonify({"message":"The platform doesn't exist"})

            currency = Currency.query.filter_by(name=data["name"], platform=data["platform"]).all()
            if len(currency) > 0:
                return jsonify({"message":"The platform already has this currency"})

            currencies_to_add.append(Currency(**data))
        # ------------------- CREATE NEW CURRENCY TO ALL PLATFORMS ---------------------- #
        else:
            platforms = Platform.query.all()
            for platform in platforms:
                currency = Currency.query.filter_by(name=data["name"], platform=platform.name).all()
                if len(currency) < 1:
                    currencies_to_add.append(Currency(name=data["name"], platform=platform.name))
        
        for currency in currencies_to_add:
            db.session.add(currency)
            db.session.commit()
        if len(currencies_to_add) > 1:
            return jsonify({"message":"Currency added to all platforms successfully!"})
        elif len(currencies_to_add) > 0:
            return jsonify({"message":"Currency added successfully!"})
        else:
            return jsonify({"message":"Currency already existing on all platforms"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- DELETE CURRENCY ---------------------- #
@platform_currency_routes.route('/currency', methods=['DELETE'])
def delete_currency():
    data = request.get_json()
    try:
        currencies_to_delete = []
        # ------------------- DELETE CURRENCY FROM ONE PLATFORM ---------------------- #
        if "platform" in data:
            platform = Platform.query.filter_by(name=data["platform"]).all()
            if len(platform) < 1:
                return jsonify({"message":"The platform doesn't exist"})

            currency = Currency.query.filter_by(name=data["name"], platform=data["platform"]).all()
            if len(currency) < 1:
                return jsonify({"message":"The platform doesn't have this currency"})

            currencies_to_delete.append(currency[0])
        # ------------------- DELETE CURRENCY FROM ALL PLATFORMS ---------------------- #
        else:
            platforms = Platform.query.all()
            for platform in platforms:
                currency = Currency.query.filter_by(name=data["name"], platform=platform.name).all()
                if len(currency) > 0:
                    currencies_to_delete.append(currency[0])
        
        for currency in currencies_to_delete:
            db.session.delete(currency)
            db.session.commit()
        if len(currencies_to_delete) > 1:
            return jsonify({"message":"Currency deleted from all platforms successfully!"})
        elif len(currencies_to_delete) > 0:
            return jsonify({"message":"Currency deleted successfully!"})
        else:
            return jsonify({"message":"Currency doesn't exist on any platform"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- GET ALL CURRENCIES ---------------------- #
@platform_currency_routes.route('/currencies', methods=['GET'])
def get_all_currencies():
    currencylist = Currency.query.all()
    currencies = []

    for currency in currencylist:
        currency = currency.__dict__
        del currency["_sa_instance_state"]
        currencies.append(currency)
    return jsonify(currencies)



# ------------------- GET CURRENCIES BY NAME ---------------------- #
@platform_currency_routes.route('/currencies/name/<name>', methods=['GET'])
def get_currencies_by_name(name):
    currencies = Currency.query.filter_by(name=name).all()
    if len(currencies) < 1:
        return jsonify({"message":"Currency doesn't exist"})
    currencylist = []
    for currency in currencies:
        currency = currency.__dict__
        currencylist.append(currency)
        del currency["_sa_instance_state"]
    return jsonify(currencylist)



# ------------------- GET CURRENCIES BY PLATFORM ---------------------- #
@platform_currency_routes.route('/currencies/platform/<name>', methods=['GET'])
def get_currencies_by_platform(name):
    currencies = Currency.query.filter_by(platform=name).all()
    if len(currencies) < 1:
        return jsonify({"message":"Currency doesn't exist"})
    currencylist = []
    for currency in currencies:
        currency = currency.__dict__
        currencylist.append(currency)
        del currency["_sa_instance_state"]
    return jsonify(currencylist)