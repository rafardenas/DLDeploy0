import os 
import sys
sys.path.append(os.getcwd())

from flask import Flask

app = Flask(__name__)

from app import routes
