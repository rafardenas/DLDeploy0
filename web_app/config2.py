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

    #MAIL_SERVER = os.environ.get('MAIL_SERVER')
    #MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    #MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    #MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    #MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['rafardenas@gmail.com']
    POSTS_PER_PAGE = 3
    MAIL_SERVER = 'smtp.googelmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = True
    MAIL_USE_SSL = True
    MAIL_DEBUG = True
    MAIL_USERNAME = 'rafardenas'
    MAIL_PASSWORD = '1Rafiqui'
    MAIL_DEFAULT_SENDER = 'rafardenas@gmail.com'


    




    