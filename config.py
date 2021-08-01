import os

import config_private


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # secret key
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'A-VERY-LONG-SECRET-KEY'

    # recaptcha public key
    RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY') or 'A-VERY-LONG-SECRET-KEY'
    RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY') or 'A-VERY-LONG-SECRET-KEY'

    # Database config
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask Gmail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    # Need to enable the less secure apps for your gmail account, here's the link:
    # https://www.google.com/settings/security/lesssecureapps
    MAIL_USERNAME = os.environ.get('GMAIL_USERNAME') or config_private.GMAIL.get('USERNAME')
    MAIL_PASSWORD = os.environ.get('GMAIL_PASSWORD') or config_private.GMAIL.get('PASSWORD')
