import re, uuid, random
import os
# Time checkers
from datetime import datetime
import time

# Requests, Generate Password and Check Password
from flask import Blueprint, jsonify, request

# Models and database
from ..extensions import db
from ..models import User, UserRole, Role
    
role_routes = Blueprint('role_routes', __name__)



# ------------------- CREATE NEW ROLE ---------------------- #
@role_routes.route('/role', methods=['POST'])
def create_role():
    data = request.get_json()
    try:
        role = Role.query.filter_by(name=data["name"]).all()
        if len(role) > 0:
            return jsonify({"message":"The given role already exists"})

        role = Role(**data)

        db.session.add(role)
        db.session.commit()
        return jsonify({"message":"Role created successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- EDIT ROLE ---------------------- #
@role_routes.route('/role', methods=['PUT'])
def edit_role():
    data = request.get_json()
    try:
        name = data["role"]
        del data["role"]
        role = Role.query.filter_by(name=name).all()
        if len(role) < 1:
            return jsonify({"message":"The given role doesn't exist"})

        role = role[0]
        for key, value in data.items():
            setattr(role, key, value)

        db.session.commit()
        return jsonify({"message":"Role updated successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- DELETE ROLE ---------------------- #
@role_routes.route('/role', methods=['DELETE'])
def delete_role():
    data = request.get_json()
    try:
        name = data["role"]
        role = Role.query.filter_by(name=name).all()
        if len(role) < 1:
            return jsonify({"message":"The given role doesn't exist"})
        role = role[0]
        db.session.delete(role)
        db.session.commit()
        return jsonify({"message":"Role deleted successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- ADD ROLE TO USER ---------------------- #
@role_routes.route('/role/user', methods=['POST'])
def add_user_role():
    data = request.get_json()
    try:
        username = data["username"]
        role = data["role"]

        user = User.query.filter_by(username=username).all()
        if len(user) < 1:
            return jsonify({"message":"Username is incorrect"})
        userId = user[0].publicId

        role = Role.query.filter_by(name=role).all()
        if len(role) < 1:
            return jsonify({"message":"Role is incorrect"})
        role = role[0].name

        userrole = UserRole(userId=userId, role=role)

        db.session.add(userrole)
        db.session.commit()
        return jsonify({"message":"Role added successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- REMOVE ROLE FROM USER ---------------------- #
@role_routes.route('/role/user', methods=['DELETE'])
def remove_user_role():
    data = request.get_json()
    try:
        username = data["username"]
        role = data["role"]

        user = User.query.filter_by(username=username).all()
        if len(user) < 1:
            return jsonify({"message":"Username is incorrect"})
        userId = user[0].publicId

        role = Role.query.filter_by(name=role).all()
        if len(role) < 1:
            return jsonify({"message":"Role is incorrect"})
        role = role[0].name

        userrole = UserRole.query.filter_by(userId=userId, role=role).all()
        if len(userrole) < 1:
            return jsonify({"message":"The user doesn't have the specified role"})
        
        userrole = userrole[0]
        db.session.delete(userrole)
        db.session.commit()
        return jsonify({"message":"Role deleted successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- GET ROLE BY NAME ---------------------- #
@role_routes.route('/role/name/<name>', methods=['GET'])
def get_role_by_name(name):
    role = Role.query.filter_by(name=name).first()
    if role == None:
        return jsonify({"message":"Role doesn't exist"})
    role = role.__dict__
    del role["_sa_instance_state"]
    return jsonify(role)



# ------------------- GET ROLE BY ID ---------------------- #
@role_routes.route('/role/id/<rid>', methods=['GET'])
def get_role_by_id(rid):
    role = Role.query.filter_by(id=rid).first()
    if role == None:
        return jsonify({"message":"Role doesn't exist"})
    role = role.__dict__
    del role["_sa_instance_state"]
    return jsonify(role)



# ------------------- GET ALL ROLES ---------------------- #
@role_routes.route('/roles', methods=['GET'])
def get_all_roles():
    rolelist = Role.query.all()
    roles = []

    for role in rolelist:
        role = role.__dict__
        del role["_sa_instance_state"]
        roles.append(role)
    return jsonify(roles)




# ------------------- GET ALL USERS BY ROLE ---------------------- #
@role_routes.route('/users/role/<name>', methods=['GET'])
def get_all_users_role(name):
    userroles = UserRole.query.filter_by(role=name).all()
    if len(userroles) < 1:
        return jsonify({"message":"The given role doesn't have users or doesn't exist"})
    users = {"role":name, "users":[]}
    for userrole in userroles:
        user = User.query.filter_by(publicId=userrole.userId).first().__dict__
        del user["_sa_instance_state"]
        users["users"].append(user)
    return jsonify(users)




# ------------------- GET ALL ROLES OF USER ---------------------- #
@role_routes.route('/roles/user/<username>', methods=['GET'])
def get_all_roles_user(username):
    user = User.query.filter_by(username=username).first()
    if user == None:
        return jsonify({"message":"User doesn't exist"})
    userroles = UserRole.query.filter_by(userId=user.publicId).all()
    if len(userroles) < 1:
        return jsonify({"message":"The given user doesn't have any role or doesn't exist"})
    roles = {"user":username, "roles":[]}

    for userrole in userroles:
        role = Role.query.filter_by(name=userrole.role).first().__dict__
        del role["_sa_instance_state"]
        roles["roles"].append(role)
    return jsonify(roles)




# ------------------- GET ALL ROLES OF USERID ---------------------- #
@role_routes.route('/roles/userid/<userid>', methods=['GET'])
def get_all_roles_user_id(userid):
    userroles = UserRole.query.filter_by(userId=userid).all()
    if len(userroles) < 1:
        return jsonify({"message":"The given user doesn't have any role or doesn't exist"})
    resultRoles = {"user":User.query.filter_by(publicId=userid).first().username, "roles":[]}
    for userrole in userroles:
        role = Role.query.filter_by(name=userrole.role).first().__dict__
        del role["_sa_instance_state"]
        resultRoles["roles"].append(role)
    return jsonify(resultRoles)
