from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_moment import Moment
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_jsglue import JSGlue

db = SQLAlchemy()
ckediter = CKEditor()
moment = Moment()
socketio = SocketIO()
login_manager = LoginManager()
bootstrap = Bootstrap()
jsglue=JSGlue()

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    user = User.query.get(int(user_id))
    return user


login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'
