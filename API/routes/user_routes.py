import re, uuid, random
import os
# Time checkers
from datetime import datetime
import time

# Check if email is valid
from validate_email import validate_email

# Requests, Generate Password and Check Password
from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash

# Models and database
from ..extensions import db
from ..models import User, Membership, Profile, ProfileMembership

# To send password email
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import jwt
from functools import wraps
    
user_routes = Blueprint('user_routes', __name__)

encryption_key = "this_is_secret" # use random strings for this, you can also set this in app.config['ENCRYPTION_KEY'], but this will also be fine

# __________________________________CHANGED HERE___________________
# a decorator for checking if the token is valid

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        #  IN THE OBJECT POSTED USE A "headers" OBJECT WITH A PARAMETER OF "x-access-token" you can google it-> send headers in the post request
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'token is missing'}), 401
        try:
            data = jwt.decode(token, encryption_key)
            _id = data['user_id']
            current_user = User.query.get(_id)
        except:
            return jsonify({'message': 'Token is Invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# ------------------- INDEX ---------------------- #
@user_routes.route('/', methods=['GET'])
def index():
    link = "https://github.com/skywallkee/SkyCryptoClub/wiki/API-available-commands-and-permissions"
    message = "Welcome on SkyCrypto.Club API Service. For documentation try: {}".format(link)
    return jsonify({"message":message})



# ------------------- LOGIN ---------------------- #
# THIS IS CHANGED TOO!
@user_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    try:
        # Get username & password
        username = data["username"]
        password = data["password"]

        # Get 2fa if given
        if "tfa" in data:
            tfa = data["tfa"]
        else:
            tfa = ""
        # _________________________________SOME CHANGES HERE TOO!______________________________
        # Check if account existing
        if not username or not password:
            return jsonify({'message': 'Could not verify'}), 401

        user = User.query.filter_by(username=username).first()

        if not user:
            return jsonify({'message': 'Could not verify'}), 401
        if check_password_hash(user.password, password):
            token = jwt.encode(
                {
                    'user_id': user.id,
                    'username': user.name, # you can add more parameters for encoding
                },
                encryption_key
            )
            return jsonify({'token': token.decode('UTF-8')})
            # Now post this token in "headers" object with parameter: 'x-access-token'
        return jsonify({'message': 'Could not verify'}), 401

        # Check if tfa is correct
        if user.otp_token == "":
            if tfa != "":
                return jsonify({"message": "Invalid 2FA Code"})
        else:
            # ------------------- TODO ---------------------- #
            # Check if tfa is valid
            pass
            # ------------------- TODO ---------------------- #

# a test route for login check

@user_routes.route('/login_test', methods=['GET', 'POST'])
@token_required
def login_test(current_user):
    # NOW YOU SIMPLY NEED TO ADD A DECORATOR OF "token_required" FOR AUTHENTICATION AFTER LOGGING IN
    # PASS "current_user" IN EVERY FUNCTION FOR ROUTES WHICH REQUIRE LOGGING IN
    return jsonify({'message': 'you can see this only if you sent the token in headers with the object'})


# ------------------- REGISTER ---------------------- #
@user_routes.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    try:
        email = data["email"]
        username = data["username"]
        password = data["password"]

        # Check if username is ok
        if len(username) < 4:
            return jsonify({"message": "Username length must be at least 4"})

        # Check if existing username
        users = User.query.filter_by(username=username).all()
        if len(users) > 0:
            return jsonify({"message": "Username already exists"})

        # Check if password is ok
        if len(password) < 6:
            return jsonify({"message": "Password must have at least 6 characters"})
        elif not re.search("[a-z]", password):
            return jsonify({"message": "Password must contain at least one small letter"})
        elif not re.search("[A-Z]", password):
            return jsonify({"message": "Password must contain at least one capital letter"})
        elif not re.search("[^a-zA-Z]", password):
            return jsonify({"message": "Password must contain at least one number or special character"})
        else:
            password = generate_password_hash(password, "sha256")

        # Check if email is ok
        if not validate_email(email):
            return jsonify({"message": "E-Mail is incorrect"})

        # Check if existing email
        users = User.query.filter_by(email=email).all()
        if len(users) > 0:
            return jsonify({"message": "E-Mail already exists"})
        
        new_user = User(publicId=str(uuid.uuid4()), email=email, username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        # ------------------- TODO ---------------------- #
        # CREATE USER A PROFILE
        # ASSIGN USER A MEMBERSHIP
        # ------------------- TODO ---------------------- #
        return jsonify({"message": "User created successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- GET ALL USERS ---------------------- #
@user_routes.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()

    out = []

    for user in users:
        user_data = user.__dict__
        del user_data["_sa_instance_state"]
        out.append(user_data)

    return jsonify(out)



# ------------------- GET USER BY ID ---------------------- #
@user_routes.route('/users/id/<userId>', methods=['GET'])
def get_user_by_id(userId):
    user = User.query.filter_by(publicId=userId).first()
    if user:
        user_data = user.__dict__
        del user_data["_sa_instance_state"]
        return jsonify(user_data)
    else:
        return jsonify({"message": "Public Id doesn't correspond to any user"})



# ------------------- GET USER BY USERNAME ---------------------- #
@user_routes.route('/users/<username>', methods=['GET'])
def get_user_by_username(username):
    user = User.query.filter_by(username=username).first()
    if user:
        user_data = user.__dict__
        del user_data["_sa_instance_state"]
        return jsonify(user_data)
    else:
        return jsonify({"message": "Username doesn't correspond to any user"})



# ------------------- CHANGE USER PASSWORD ---------------------- #
@user_routes.route('/user/password', methods=['POST'])
def change_user_password():
    data = request.get_json()
    try:
        username = data["username"]
        password = data["password"]
        new_password = data["new_password"]
        user = User.query.filter_by(username=username).first()
        if check_password_hash(user.password, password) == False:
            return jsonify({"message": "Incorrect Password"})
        elif len(new_password) < 6:
            return jsonify({"message": "New Password must have at least 6 characters"})
        elif not re.search("[a-z]", new_password):
            return jsonify({"message": "New Password must contain at least one small letter"})
        elif not re.search("[A-Z]", new_password):
            return jsonify({"message": "New Password must contain at least one capital letter"})
        elif not re.search("[^a-zA-Z]", new_password):
            return jsonify({"message": "New Password must contain at least one number or special character"})
        else:
            new_password = generate_password_hash(new_password, "sha256")
        user.password = new_password
        db.session.commit()
        return jsonify({"message": "Password changed successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- RESET FORGOTTEN USER PASSWORD ---------------------- #
@user_routes.route('/user/password/reset', methods=['POST'])
def reset_user_password():
    data = request.get_json()
    try:
        username = data["username"]
        # Check if user did reset his password in the past 10 minutes
        user = User.query.filter_by(username=username).first()
        last_reset = time.mktime(user.last_pass_reset.timetuple())
        now = time.mktime(datetime.now().timetuple())
        if int(now - last_reset) / 60 < 5:
           return jsonify({"message":"Can only reset once every 5 minutes"})

        # GENERATE RANDOM PASSWORD
        small_letters = "abcdefghijklmnopqrstuvwxyz"
        big_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        numbers = "01234567890"
        characters = "!@#$%^&*()?"

        new_password =  "".join(random.sample(small_letters, random.randint(5, 8))) +\
                        "".join(random.sample(big_letters, random.randint(5, 8))) +\
                        "".join(random.sample(numbers, random.randint(3, 5))) +\
                        "".join(random.sample(characters, random.randint(2, 4)))

        new_password = "".join(random.sample(new_password, len(new_password)))

        # Send Email with not hashed password
        sender_email = os.environ.get('MAIL_USER')
        receiver_email = user.email
        password = os.environ.get('MAIL_PASS')

        message = MIMEMultipart("alternative")
        message["Subject"] = "Password Recovery"
        message["From"] = sender_email
        message["To"] = receiver_email

        text = """Your new password is:\
        {}""".format(new_password)
        html = """\
        <html>
        <body>
            <h1>New Password</h1>
            {}
        </body>
        </html>
        """.format(new_password)

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)

        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("mail.privateemail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        

        # Set password to account
        new_password = generate_password_hash(new_password, "sha256")

        user.password = new_password
        user.last_pass_reset = datetime.now()
        db.session.commit()

        return jsonify({"message": "Password changed successfully!"})
    except Exception as e:
        if str(e).contains("Connection unexpectedly closed"):
            return jsonify({"message":str(e) + ". Try again."})
        else:
            return jsonify({"message":str(e)})



# ------------------- CHANGE USER EMAIL ---------------------- #
@user_routes.route('/user/email', methods=['POST'])
def change_user_email():
    data = request.get_json()
    try:
        username = data["username"]
        password = data["password"]
        new_email = data["new_email"]
        user = User.query.filter_by(username=username).first()

        if check_password_hash(user.password, password) == False:
            return jsonify({"message": "Incorrect Password"})
        
        # Check if email is ok
        if not validate_email(new_email):
            return jsonify({"message": "E-Mail is incorrect"})

        # Check if existing email
        users = User.query.filter_by(email=new_email).all()
        if len(users) > 0:
            return jsonify({"message": "E-Mail already exists"})

        user.email = new_email
        db.session.commit()
        return jsonify({"message": "E-Mail changed successfully!"})
    except Exception as e:
        return jsonify({"message":str(e)})



# ------------------- ACTIVATE 2FA ---------------------- #
@user_routes.route('/user/tfa', methods=['POST'])
def activate_tfa():
    data = request.get_json()

    # ------------------- TODO ---------------------- #
    # MAKE 2FA
    # ------------------- TODO ---------------------- #
    return jsonify({"message":"2FA CURRENTLY ISN'T AVAILABLE"})