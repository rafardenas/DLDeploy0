import os 
import sys
#sys.path.append(os.getcwd())
#sys.path.append('..')
#sys.path.append('.')

from flask import Flask
from web_app.config2 import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager



app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.init_app(app)
login.login_view = "login"
from web_app.app import routes, models
#db.create_all()
#db.drop_all()




