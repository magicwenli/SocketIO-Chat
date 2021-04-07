from flask import render_template, flash, redirect, url_for, Blueprint
from flask_login import login_user, logout_user, login_required, current_user

from app.extends import db
from app.forms import LoginForm, RegisterForm
from app.models import User
from app.utils import redirect_back

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('chat.index'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        users = User.query.all()
        user = User.query.first()
        has_user = False
        for user in users:
            if username == user.username:
                has_user = True
                break
        if has_user and user.validate_password(password):
            login_user(user, remember)
            flash('Welcome back.', 'info')
            return redirect(url_for('chat.index'))
        else:
            flash('Invalid username or password.', 'warning')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout success.', 'info')
    return redirect_back()


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        about = form.about.data
        if User.query.filter(User.username == username).first():
            flash('Username have been taken, choose another one.')
        else:
            user = User(username=username, about=about)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('User Created.', 'success')
            return redirect(url_for('chat.index'))
    return render_template('auth/register.html', form=form)
