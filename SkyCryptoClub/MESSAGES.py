# PASSWORD RECOVERY
PASSWORD_RESET_SUCCESS_TITLE = 'A mail with the new password has been sent on the given email.'
PASSWORD_RESET_SUCCESS_MESSAGE = "If you don't receive any mail, please try to contact our support."
PASSWORD_RESET_FAIL_TITLE = 'There is no account with the given username or email.'
PASSWORD_RESET_FAIL_MESSAGE = "If you need more help, please try to contact our support."

# REGISTRATION
REGISTER_ERROR   = {
                    'error': {
                        'title': 'Invalid Username or E-Mail',
                        'message': "The given Username or E-Mail are invalid or might be already in use."
                    }}
REGISTER_SUCCESS = {
                    'created': {
                        'title': 'Account created successfully! Please check your E-Mail for the Password',
                        'message': "If you don't receive any E-Mail, please try the Forgot Password form or contact our support."
                    }}

# TFA MAIL MESSAGES
TFA_SUBJECT = "2FA Key"
TFA_TEXT = """Your 2FA key is:\
{}"""
TFA_HTML = """\
<html>
<body>
<h1>Your 2FA key is:</h1>
{}
</body>
</html>
"""


# REGISTER MAIL MESSAGES
REGISTER_SUBJECT = "Account Registration"
REGISTER_TEXT = """Your Account is:\
Email: {}\
Username: {}\
Password: {}"""
REGISTER_HTML = """\
<html>
<body>
<h1>Your Account is:</h1>
Email: {}<br />
Username: {}<br />
Password: {}<br />
</body>
</html>
"""


# PASSWORD RECOVERY MAIL MESSAGES
RECOVERY_SUBJECT = "Account Recovery"
RECOVERY_TEXT = """Your Account is:\
Email: {}\
Username: {}\
Password: {}"""
RECOVERY_HTML = """\
<html>
<body>
<h1>Your Account is:</h1>
Email: {}<br />
Username: {}<br />
Password: {}<br />
</body>
</html>
"""


# LINKED ACCOUNTS
ACCOUNT_UNLINK_TITLE_SUCCESS = "Deletion successfull!"
ACCOUNT_UNLINK_MESSAGE_SUCCESS = "The selected account has been successfully removed!"
ACCOUNT_UNLINK_TITLE_FAIL = "Deletion unsuccessfull!"
ACCOUNT_UNLINK_MESSAGE_FAIL = "The selected account has not been removed!"