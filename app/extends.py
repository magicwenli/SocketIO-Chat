import logging.handlers

from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_jsglue import JSGlue
from flask_login import LoginManager
from flask_moment import Moment
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
ckediter = CKEditor()
moment = Moment()
socketio = SocketIO()
login_manager = LoginManager()
bootstrap = Bootstrap()
jsglue = JSGlue()


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    user = User.query.get(int(user_id))
    return user


login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'

# set logger
LOG_FILENAME = 'running.log'
logger = logging.getLogger()

logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILENAME, maxBytes=10485760, backupCount=5, encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
