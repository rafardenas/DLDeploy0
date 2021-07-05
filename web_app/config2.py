import os
import sys
#sys.path.append(os.getcwd())
#sys.path.append('.')
#basedir = os.path.abspath(os.path.dirname(__file__))
basedir = os.path.abspath(".")

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    print(SQLALCHEMY_DATABASE_URI)
    #print(os.environ.get('DATABASE_URL'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    