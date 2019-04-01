from nativ import app
import os
import sys


basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
resourcedir = os.path.abspath(os.path.dirname(__file__))

prefix = 'sqlite:////'
SECRET_KEY = os.getenv('SECRET_KEY', 'secret string')
SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'data-dev.db')
# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://bosonUser:Bishe2019@localhost:3306/boson'
SQLALCHEMY_TRACK_MODIFICATIONS = False
BOSON_POST_PER_PAGE = 10
BOSON_COMMENT_PER_PAGE = 5

BOSON_API_TOKEN = 'E3fukuEs.33290.s6Q5yXydhI8I'
# BOSON_API_TOKEN = 'zbf_7Bcy.33431.YmVh3hdoLWhd'


AVATAR_FOLDER = os.path.join(resourcedir, 'static/avatar')

ADMINS = ['910996309@qq.com']
# MAIL_SERVER = 'localhost'
# MAIL_PORT = 8025
# MAIL_SERVER = 'smtp.googlemail.com'
# MAIL_PORT = 587
# MAIL_USE_TLS = 1
# MAIL_USERNAME = 'hxdarrow@gamil.com'
# MAIL_PASSWORD = 'Xx3015783'

MAIL_SERVER='smtp.qq.com'
MAIL_PORT=465
MAIL_USE_SSL=1
MAIL_USE_TLS=0
MAIL_USERNAME='910996309@qq.com'
MAIL_PASSWORD='ftsmmhbfctiqbchi'



