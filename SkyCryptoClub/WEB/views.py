# RESPONSES
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.template import loader

# TIME
from django.utils import timezone
import time

# MODELS
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from ..API.models import TwoFactorLogin, User, FAQCategory, Question, Profile, Statistics, \
                         Platform, PlatformCurrency, Wallet, Account, AccountKey
from django.contrib.auth import get_user_model

# EMAIL
from validate_email import validate_email
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# MULTI-PROCESS
from multiprocessing import Process

# GLOBAL VARIABLES
from ..GLOBAL import EMAIL as gEMAIL, PASSWORD as gPASSWORD, STAKE_TOKEN

# VALIDATION
from django.core.files.images import get_image_dimensions
from .validator import valid_login, valid_tfa, valid_register

# STRING
import string

# RANDOM
import random


# Functionality: User Log Out Function
# Description: If the user is logged in, the function
#              will log him out and redirect to the index 
# Data input: user - User model
# Data output: redirect to index
@login_required
def user_logout(request):
    # Check if user is authenticated to log out
    if request.user.is_authenticated:
        logout(request)
    # Redirect  the user to index
    return HttpResponseRedirect(reverse('index'))


# Functionality: Index Page
# Description: Returns the index page to the user
def index(request):
    # Load the index template and the context
    template    = loader.get_template('WEB/index.html')
    large_number = random.randint(1, 15)
    medium_number = random.randint(1, 16)
    small_number = random.randint(1, 2)
    context     = {"stake_large": "/images/partners/stake/large{}.gif".format(large_number),
                   "stake_medium": "/images/partners/stake/medium{}.gif".format(medium_number),
                   "stake_small": "/images/partners/stake/small{}.gif".format(small_number)}
    # Return the template
    return HttpResponse(template.render(context, request))


# Functionality: Login Page
# Description: If the user is not authenticated, display the 
#              log in page; when the data is sent, process it
#              and log the user. If the user is authenticated
#              then redirect him to the index page.
# Data input: username - username given by user
#             password - password given by user
def user_login(request):
    # If user is authenticated redirect him to index
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))

    # If the page is accessed
    if request.method == 'GET':
        # Load the login template and the context
        template    = loader.get_template('registration/login.html')
        context     = {}
        # Return the template
        return HttpResponse(template.render(context, request))

    # If the user submitted the login form
    elif request.method == "POST":
        # Get the username, password and 2FA
        username    = request.POST.get('username')
        password    = request.POST.get('password')
        tfa         = request.POST.get('2FA')

        # Check if the username, password and 2FA are valid
        if not valid_login(username, password):
            return HttpResponseRedirect(reverse('login'))
        
        user = authenticate(username=username, password=password)
        
        if user is None or not valid_tfa(user, tfa):
            return HttpResponseRedirect(reverse('login'))

        # Log in the user
        login(request, user)

        # Redirect the user to the index
        return HttpResponseRedirect(reverse('index'))

    # If none of the above methods are called, 
    # redirect the user to index
    else:
        return HttpResponseRedirect(reverse('index'))


# Functionality: Send E-Mail with the Password
# Description: Sends via smtplib an E-Mail to the user
#              with the given un-hashed password.
# Data input: email     - user's email, 
#             username  - user's username  
#             userpass  - user's password
def send_password_mail(email, username, userpass):
    # Load mail data
    sender_email    = gEMAIL
    password        = gPASSWORD
    receiver_email  = email

    # Load mail body
    text = """Your Account is:\
            Email: {}\
            Username: {}\
            Password: {}""".format(email, username, userpass)
    html = """\
            <html>
            <body>
                <h1>Your Account is:</h1>
                Email: {}<br />
                Username: {}<br />
                Password: {}<br />
            </body>
            </html>
            """.format(email, username, userpass)

    # Set mail data
    message             = MIMEMultipart("alternative")
    message["Subject"]  = "Account Password"
    message["From"]     = sender_email
    message["To"]       = receiver_email

    # Set Mail Body
    part1   = MIMEText(text, "plain")
    part2   = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)

    # Set secure connection
    context = ssl.create_default_context()

    # Try sending mail until the mail has been sent
    while True:
        try:
            with smtplib.SMTP_SSL("mail.privateemail.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message.as_string())
        except Exception as e:
            print("Couldn't send password mail: ", e)
            time.sleep(5)
            continue
        break


# Functionality: Register Page
# Description: If the user is not authenticated, display the 
#              registration page; when the data is sent, process it,
#              create a password and send it through email. 
#              If the user is authenticated then redirect him to 
#              the index page.
# Data input: username  - user's given username
#             email     - user's given password
def user_register(request):
    # If user is authenticated redirect him to index
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))

    # Load the register template and the context
    template    = loader.get_template('registration/register.html')
    context     = {}

    # If the user has submitted the register form
    if request.method == 'POST':
        # Get the username and email
        username    = request.POST.get('username')
        email       = request.POST.get('email')

        # Validate the username and email
        if valid_register(username, email):
            # Create a random password out of letters and digits
            characters      = string.ascii_letters + string.digits
            stringLength    = 20
            password        = ''.join(random.choice(characters) for i in range(stringLength)).replace(" ", "")

            # Create the registered user
            User.objects.create_user(username, email, password)

            # Send the generated password through email on a different process
            send_mail_process = Process(target=send_password_mail, args=(email, username, password,))
            send_mail_process.start()

            # Set notification message
            context['created'] = {'title': 'Account created successfully! Please check your E-Mail for the Password',
                                'message': "If you don't receive any E-Mail, \
                                            please try the Forgot Password form or contact our support."}
        else:
            context['error'] = {'title': 'Invalid Username or E-Mail',
                              'message': "The given Username or E-Mail are invalid or might be already in use."}

    # Return the template
    return HttpResponse(template.render(context, request))


# Functionality: Password Recovery Page
# Description: If the user is not authenticated, redirect him
#              redirect him to the index page. If the request
#              method is GET then display the password recovery
#              page. If the request method is POST, then check
#              if the user's username and email exist and are matching
# Data input: username - user's given username
#             email    - user's given email
def recover_password(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        user = User.objects.filter(username=username, email=email)
        if len(user) == 1:
            import string
            import random
            characters = string.ascii_letters + string.digits + string.punctuation
            stringLength = 20
            password = ''.join(random.choice(characters) for i in range(stringLength)).replace(" ", "")
            user = user.first()
            user.set_password(password)
            user.save()
            send_mail_process = Process(target=send_password_mail, args=(user.email, user.username, password,))
            send_mail_process.start()
            context = {
                'page': 'login',
                'found': 'True',
                'title': 'A mail with the new password has been sent on the given email.',
                'message': "If you don't receive any mail, please try to contact our support.",
                'type': 'success'
            }
        else:
            context = {
                'page': 'login',
                'found': 'True',
                'title': 'There is no account with the given username or email.',
                'message': "If you need more help, please try to contact our support.",
                'type': 'danger'
            }
        return render(request, 'registration/recover_password.html', context)
    else:
        return render(request, 'registration/recover_password.html', {'page': 'login'})


# Functionality: FAQ Page
# Description: Displays all the categories, questions and
#              answers in the FAQ template
def faq(request):
    categories = FAQCategory.objects.all()
    answers = Question.objects.filter(accepted=True)
    context = {"categories": categories, "answers": answers}
    return render(request, 'WEB/faq.html', context)


# Functionality: Terms & Conditions Page
# Description: Displays the terms template
def terms(request):
    context = {}
    return render(request, 'WEB/terms.html', context)


# Functionality: Dashboard Profile Page
def dashboard(request):
    return HttpResponseRedirect('/dashboard/{}'.format(request.user.username))


# Functionality: Dashboard User Profile Page
# Description: Displays another user's profile page
def dashboard_user(request, username):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    user = get_user_model().objects.filter(username=username)
    if len(user) == 0:
        return HttpResponseRedirect(reverse('dashboard'))
    user = user.first()
    is_owner = False
    if user.username == request.user.username:
        is_owner = True
    profile = Profile.objects.filter(user=user).first()
    statistics = Statistics.objects.filter(profile=profile).first() if profile.publicStats == True or is_owner else None
    titles = {
        'Newbie': (0, 100),
        'Novice': (100, 200),
        'Initiate': (201, 750),
        'Adept': (751, 1000),
        'Member': (1001, 2500),
        'Master': (2501, 5000),
        'Chief': (10001, 50000),
        'Veteran': (50001, 100000),
        'VIP': (100001, 1500000),
        'Lord': (1500001, float("inf"))
    }
    title = ""
    if profile.publicLevel or is_owner:
        for t in titles:
            if titles[t][0] <= profile.level and profile.level <= titles[t][1]:
                title = t
                break
    userWallets = Wallet.objects.filter(profile=profile)
    wallets = {}
    platforms = Platform.objects.all()
    for platform in platforms:
        currencies = PlatformCurrency.objects.filter(platform=platform)

    context = {'profile': profile,
               'statistics': statistics,
               'title': title,
               'platforms': platforms,
               'owner': is_owner}
    return render(request, 'dashboard/profile.html', context)


# Functionality: Validate Image Size
# Description: Checks if the image size is under
#              the specified limit
# Data input: 
# Data output: 
def image_size(value):
    limit = 3 * 1024 * 1024
    print(value.size)
    if value.size > limit:
        return 400
    return 200


# Functionality: Validate Image Dimensions
# Description: Checks if the image is between the
#              minimum and maximum dimensions with
#              equal length and height
def image_dimensions(value):
    minLength = 150
    maxLength = 500
    width, height = get_image_dimensions(value)
    print(width, height)
    if width != height or width < minLength or width > maxLength:
        return 400
    return 200


# Functionality: Profile Settings Page
# Description: If the user is not authenticated, redirects
#              the user to the index page. If the method is
#              GET then displays the Profile Settings template
#              If the method is POST then check if the user
#              tried modifying his avatar or password/email.
#              If the modified data is valid, then change it
def settings(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()
    context = {'profile': profile,
               'platforms': platforms}
    if request.method == "POST":
        if "updateAvatar" in request.POST:
            avatar = request.FILES['newAvatar']
            ok = True
            if image_size(avatar) == 400:
                context["sizeError"] = {'title': 'File too large!', 'message': 'Size should not exceed 3 MiB.'}
                ok = False
            if image_dimensions(avatar) == 400:
                context["dimensionsError"] = {'title': 'Incorrect dimensions!', 'message': 'Image width and height must be equal. \
                                                                    The image should be at least 150x150 and not more than 500x500'}
                ok = False

            if ok:
                profile.avatar = avatar
                profile.save()
                context["changedAvatar"] = {"title": "Success!", "message": "The Avatar has been changed successfully!"}
        else:
            email = request.POST.get("email")
            password = request.POST.get("password")
            newpass = request.POST.get("newpass")
            newpassconfirm = request.POST.get("newpassconfirm")
            error = False
            if not request.user.check_password(password):
                context["passError"] = {"title": "Invalid password", "message": "The given password is not corect!"}
                error = True
            if 0 < len(newpass) and len(newpass) < 6:
                context["newPassError"] = {"title": "Password too weak", "message": "The new password must have at least 6 characters!"}
                error = True
            elif newpass != newpassconfirm:
                context["newPassError"] = {"title": "Incorrect New Password", "message": "The new password doesn't match with the confirmation!"}
                error = True
            
            if not error:
                if email != request.user.email:
                    request.user.email = email
                    request.user.save()
                    context["changedEmail"] = {"title": "Success!", "message": "The E-Mail has been changed successfully!"}
                if len(newpass) > 0:
                    request.user.set_password(newpass)
                    request.user.save()
                    context["changedPassword"] = {"title": "Success!", "message": "The Password has been changed successfully!"}
    return render(request, 'settings/settings.html', context)


# Functionality: Privacy Settings Page
# Description: If the user is not authenticated, redirects
#              him to the index page. If the method is GET, then
#              displays the privacy template. If the method is
#              POST then get the user's given privacy settings and
#              set them
def privacy(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()
    context = {'profile': profile,
               'platforms': platforms}
    if request.method == "POST":
        publicStats = True if request.POST.get("publicStats") == "true" else False
        publicLevel = True if request.POST.get("publicLevel") == "true" else False
        publicXP = True if request.POST.get("publicXP") == "true" else False
        publicName = True if request.POST.get("publicName") == "true" else False
        profile.publicStats = publicStats
        profile.publicLevel = publicLevel
        profile.publicXP = publicXP
        profile.publicName = publicName
        profile.save()
    return render(request, 'settings/privacy.html', context)


# Functionality: Find User's ID on Stake.com
# Description: Makes a query request to stake api with
#              user's username and finds user's ID
def find_user_id_stake(username):
    import requests
    url = "https://api.stake.com/graphql"
    payload = "{\"query\":\"query {\\n user(name: \\\"" + username + "\\\") {\\n id\\n}\\n}\"}"
    headers = {
    'Content-Type': 'application/json',
    'x-access-token': STAKE_TOKEN,
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data = payload)
    user = response.json()["data"]["user"]
    if "id" in user:
        return user["id"]
    else:
        return None


# Functionality: Send a Message on Stake
# Description: Finds user's ID on Stake and makes
#              a mutation request to send a message to
#              the user
def send_message_stake(account, message):
    userId = find_user_id_stake(account.username)
    if userId is None:
        return None
    else:
        import requests
        url = "https://api.stake.com/graphql"
        payload = "{\"query\":\"mutation {\\n sendMessage(userId: \\\"" + userId + "\\\", message: \\\"" + message + "\\\") {\\n id}}\"}"
        headers = {
        'Content-Type': 'application/json',
        'x-access-token': STAKE_TOKEN,
        'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data = payload)
        print(response.json(), payload)
        return 200


# Functionality: Send User Message
# Description: Checks account's platform and sends
#              a given message on that platform to the
#              given user
def send_message(account, message):
    if account.platform.name == "Stake":
        response = send_message_stake(account, message)
        if response is None:
            return None
        else:
            return 200


# Functionality: Linked Accounts Settings Page
# Description: If the user is not authenticated, redirects
#              him to the index page. If the method is get
#              displays the linked template. If the method
#              is post then check if the user wanted to remove
#              an account, add a new one or confirm a token.
#              Removing an account will get the id of the account;
#              Adding a new account will send a message with a token
#              on the given platform to the account; Confirming a
#              token will check the unique token in the database and
#              erase it if matching
def linked(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    profile = Profile.objects.filter(user=request.user).first()
    platforms = Platform.objects.all()
    linked = Account.objects.filter(profile=profile)
    context = {'profile': profile, 'linked': linked, 'platforms': platforms}
    if request.method == "POST":
        if 'removeAccount' in request.POST:
            id = request.POST.get('accountId')
            if id:
                account = Account.objects.filter(id=id)
                account.delete()
                context["success"] = {"title": "Deletion successfull!", "message": "The selected account has been successfully removed!"}
        if 'requestToken' in request.POST:
            username = request.POST.get('accountUsername')
            platformId = request.POST.get('accountPlatform')
            if username and platformId:
                platform = Platform.objects.filter(id=platformId).first()
                if len(Account.objects.filter(profile=profile, platform=platform, username=username)) == 0:
                    account = Account.objects.create(profile=profile, platform=platform, username=username)
                    key = AccountKey.objects.filter(account=account).first()
                    message = "Your key is: " + key.key
                    response = send_message(account, message)
                    if response is None:
                        context["danger"] = {"title": "Account doesn't exist!", "message": "The given account doesn't exist on the given platform!"}
                        account.delete()
                        key.delete()
                    else:
                        context["success"] = {"title": "Account added successfully!", "message": "The given account has been added! A confirmation \
                                                                                    token has been sent on your account. Please make sure that you can \
                                                                                    receive private messages on the selected platform. If not, enable them or \
                                                                                    add skyBot to your friends list and request the token again!"}
                elif not Account.objects.filter(profile=profile, platform=platform, username=username).first().active:
                    account = Account.objects.filter(profile=profile, platform=platform, username=username).first()
                    account.profile = profile
                    account.save()
                    key = AccountKey.objects.filter(account=account).first()
                    message = "Your key is: " + key.key
                    response = send_message(account, message)
                    if response is None:
                        context["danger"] = {"title": "Account doesn't exist!", "message": "The given account doesn't exist on the given platform!"}
                        account.delete()
                        key.delete()
                    else:
                        context["success"] = {"title": "Account added successfully!", "message": "The given account has been added! A confirmation \
                                                                                token has been sent on your account. Please make sure that you can \
                                                                                receive private messages on the selected platform. If not, enable them or \
                                                                                add skyBot to your friends list and request the token again!"}
                else:
                    context["danger"] = {"title": "Account already activated", "message": "The given account has already been activated on your account!"}
        if 'addAccount' in request.POST:
            token = request.POST.get('accountToken')
            key = AccountKey.objects.filter(key=token)
            if len(key) == 1:
                key = key.first()
                key.account.active = True
                key.account.save()
                key.delete()
                context["success"] = {"title": "Account activated successfully!", "message": "The given account has been successfully activated!"}
            else:
                context["danger"] = {"title": "Account wasn't activated", "message": "The given token doesn't correspond to any account!"}
    return render(request, 'settings/linked.html', context)