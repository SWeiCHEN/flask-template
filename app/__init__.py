import sqlalchemy as sqlalchemy
from flask import Flask
# from flask-bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail


from config import Config


app = Flask(__name__)
# bootstrap = Bootstrap(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login = LoginManager(app)
login.login_view = 'sign_in' # set the sing_in() in routes.py be the sign_in page
login.login_message = 'You must login to access this page'
login.login_message_category = 'info'
mail = Mail(app)

from app.routes import *
