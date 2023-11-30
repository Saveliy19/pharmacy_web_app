from flask import Flask
from config import Config
from flask_login import LoginManager

app = Flask(__name__, static_folder="D:/Kursachi/AptekaRU/static")
app.config.from_object(Config)
login = LoginManager(app)
login.login_view = 'login'

from app.routes import app

