import os
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
migrate = Migrate()

app_path = os.path.abspath(os.path.dirname(__file__))
CERTIFICATE_FOLDER = os.path.join(app_path, 'main/certs')

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['CERTIFICATE_FOLDER'] = CERTIFICATE_FOLDER

    if not os.path.exists(app.config['CERTIFICATE_FOLDER']):
        os.mkdir(app.config['CERTIFICATE_FOLDER'])

    db.init_app(app)
    migrate.init_app(app, db)

    from app.main import bp as cert_bp
    app.register_blueprint(cert_bp)

    from app import models

    return app
