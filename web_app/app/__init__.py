import os 
import sys
sys.path.append(os.getcwd())
sys.path.append('..')
#sys.path.append('.')

from flask import Flask
from web_app.config2 import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
from web_app.app import routes, models
migrate = Migrate(app, db)
#db.create_all()
#db.drop_all()




