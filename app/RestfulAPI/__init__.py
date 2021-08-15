from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' # 'sqlite:///' + os.path.join(basedir, 'app.db')
    db.init_app(app)
    from .routes import main
    app.register_blueprint(main)

    return app