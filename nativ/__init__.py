from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
from flask_ckeditor import CKEditor
from flask_wtf import CSRFProtect
from flask_dropzone import Dropzone
from flask_mail import Mail
from bosonnlp import BosonNLP


app = Flask('nativ')
app.config.from_pyfile('settings.py')
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

bootstrap = Bootstrap(app)
login_manager = LoginManager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
moment = Moment(app)
ckeditor = CKEditor(app)
csrf = CSRFProtect(app)
dropzone = Dropzone(app)
nlp = BosonNLP(app.config['BOSON_API_TOKEN'])
mail = Mail(app)

login_manager.login_view = 'login'
login_manager.login_message = '请您先登陆'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    from nativ.models import User
    user = User.query.get(int(user_id))
    return user

from nativ import views, commands