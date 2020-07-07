MESSAGES = {
    "en": {
        # PASSWORD RESET
        "PASSWORD_RESET": {
            "SUCCESS": {
                "type": "success",
                "title": "Password successfully reseted!",
                "message": "A mail with the new password has been sent to your email. If you don't receive any mail, please try to contact our support."
            }, 
            "FAIL": {
                "type": "danger",
                "title": "Failed to reset the password!",
                "message": "There is no account with the given username and email. If you need more help, please try to contact our support."
            }
        },
        # REGISTRATION
        "REGISTER": {
            "SUCCESS": {
                "type": "success",
                "title": "Account created successfully! Please check your E-Mail for the Password!",
                "message": "If you don't receive any E-Mail, please try the Forgot Password form or contact our support."
            },
            "FAIL": {
                "type": "danger",
                "title": "Invalid Username or E-Mail!",
                "message": "The given Username or E-Mail are invalid or might be already in user."
            }
        },
        # ACCOUNT LINKING
        "ACCOUNT_UNLINK": {
            "SUCCESS": {
                "type": "success",
                "title": "Unlink successful!",
                "message": "The selected account has been successfully unlinked."
            },
            "FAIL": {
                "type": "danger",
                "title": "Failed to unlink!",
                "message": "We were not able to unlink the given account. Please contact the support."
            }
        },
        "ACCOUNT_LINK": {
            "SUCCESS": {
                "type": "success",
                "title": "Account linked successfully!",
                "message": "The given account has been successfully linked."
            },
            "FAIL": {
                "INVALID_API": {
                    "type": "danger",
                    "title": "Account wasn't linked!",
                    "message": "The given API Key doesn't match the provided username."
                },
                "ALREADY_LINKED": {
                    "type": "danger",
                    "title": "Account wasn't linked!",
                    "message": "The given account is already linked with another profile."
                }
            }
        },
        # CONTACT PAGE
        "CONTACT_US": {
            "SUCCESS": {
                "type": "success",
                "title": "Message sent!",
                "message": "The message has been sent! <br/>We will try to respond as soon as possible."
            },
            "FAIL": {
                "type": "danger",
                "title": "Invalid Data!",
                "message": "Please input an email, subject and message."
            }
        },
        # SETTINGS PAGE
        "AVATAR": {
            "SUCCESS": {
                "type": "success",
                "title": "Success!",
                "message": "The Avatar has been changed successfully!"
            },
            "FAIL": {
                "LARGE_IMAGE": {
                    "type": "danger",
                    "title": "File too large!",
                    "message": "Size should not exceed 3 MiB."
                },
                "DIMENSIONS": {
                    "type": "danger",
                    "title": "Incorrect dimensions!",
                    "message": "Image width and height must be equal. \
                                The image should be at least 150x150 and not more than 500x500."
                },
                "NO_IMAGE": {
                    "type": "danger",
                    "title": "No image!",
                    "message": "You must provide an image to set as an avatar."
                }
            }
        },
        "PRIVACY": {
            "SUCCESS": {
                "type": "success",
                "title": "Success!",
                "message": "The Privacy settings have been changed successfully."
            }
        },
        "PASSWORD": {
            "SUCCESS": {
                "type": "success",
                "title": "Success!",
                "message": "The Password has been changed successfully."
            },
            "FAIL": {
                "NOT_MATCHING": {
                    "type": "danger",
                    "title": "Incorrect Confirmation Password!",
                    "message": "The new password doesn't match with the confirmation."
                },
                "SHORT": {
                    "type": "danger",
                    "title": "Password too weak!",
                    "message": "The new password must have at least 6 characters."
                },
                "INCORRECT": {
                    "type": "danger",
                    "title": "Invalid password!",
                    "message": "The given password is not corect."
                }
            }
        },
        "EMAIL": {
            "SUCCESS": {
                "type": "success",
                "title": "Success!",
                "message": "The E-Mail has been changed successfully."
            },
            "FAIL": {
                "EXISTING": {
                    "type": "danger",
                    "title": "Existing E-Mail",
                    "message": "The given E-Mail address is already in use by another user!"
                },
            }
        },
        "TWO_FACTOR": {
            "SUCCESS": {
                "type": "success",
                "title": "Success!",
                "message": "The Two Factor has been changed successfully."
            },
            "FAIL": {
                "type": "danger",
                "title": "Invalid Two Factor",
                "message": "The value of the Two Factor input is invalid!"
            }
        },
        "INVALID_INPUT": {
            "type": "danger",
            "title": "Invalid Input!",
            "message": "Please send only the data available in the form and complete all inputs."
        },
        # EXCHANGES
        "EMPTY_EXCHANGE_TABLE": "There are no opened Exchange Requests",
        "INVALID_PAGE": {
            "type": "danger",
            "title": "Invalid Page!",
            "message": "The requested page does not exist."
        },
        "EXCHANGE_REQUEST": {
            "FAIL": {
                "type": "danger",
                "title": "Insufficient funds!",
                "message": "You don't own enough funds in the given balance."
            }
        },
        # SUPPORT
        "CREATE_TICKET": {
            "FAIL": {
                "MISSING_TITLE": {
                    "type": "danger",
                    "title": "Missing title!",
                    "message": "Please input a title for the ticket."
                },
                "TITLE_LENGTH": {
                    "type": "danger",
                    "title": "Title length error!",
                    "message": "Please give a suggestive title with no more than 60 characters."
                },
                "MISSING_CATEGORY": {
                    "type": "danger",
                    "title": "Missing category!",
                    "message": "The category should match your problem, if no category is appropiate, choose \"Others\"."
                },
                "INVALID_CATEGORY": {
                    "type": "danger",
                    "title": "Invalid category!",
                    "message": "The category should match your problem, if no category is appropiate, choose \"Others\"."
                },
                "MISSING_MESSAGE": {
                    "type": "danger",
                    "title": "Missing message!",
                    "message": "The message should describe your problem as detailed as possible."
                },
                "SHORT_MESSAGE": {
                    "type": "danger",
                    "title": "Please input a more detailed message!",
                    "message": "The message should describe your problem as detailed as possible."
                }
            }
        },
        # LOGIN
        "TFA_MAIL": {
            "SUBJECT": "2FA Key",
            "MESSAGE": "Your 2FA key is: {}",
            "HTML": """\
                    <html>
                        <body>
                            <h1>Your 2FA key is:</h1>
                            {}
                        </body>
                    </html>
                    """
        },
        "REGISTER_MAIL": {
            "SUBJECT": "Account Registration",
            "MESSAGE": """Your Account is:\n\
                          Email: {}\
                          Username: {}\
                          Password: {}""",
            "HTML": """\
                    <html>
                        <body>
                            <h1>Your Account is:</h1>
                            Email: {}<br />
                            Username: {}<br />
                            Password: {}<br />
                        </body>
                    </html>
                    """
        },
        "RECOVERY_MAIL": {
            "SUBJECT": "Account Recovery",
            "MESSAGE": """Your Account is:\
                          Email: {}\
                          Username: {}\
                          Password: {}""",
            "HTML": """\
                    <html>
                        <body>
                            <h1>Your Account is:</h1>
                            Email: {}<br />
                            Username: {}<br />
                            Password: {}<br />
                        </body>
                    </html>
                    """
        }
    },
}