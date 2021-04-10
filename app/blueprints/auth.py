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
        return redirect(url_for('chat.home'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember = form.remember.data
        user = User.query.filter_by(email = email).first()
        if user is not None:
            if user.verify_password(password):
                login_user(user, remember)
                return redirect(url_for('chat.home'))
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
    if current_user.is_authenticated:
        return redirect(url_for('chat.home'))

    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        username = form.username.data
        password = form.password.data
        about = form.about.data
        if User.query.filter_by(email = email).first():
            flash('This email have been registered, please log in.')
        elif User.query.filter_by(username = username).first():
            flash('Username have been taken, choose another one.')
        else:
            user = User(username=username, email=email, about=about)
            user.set_password(password)
            user.generate_email_hash()
            db.session.add(user)
            db.session.commit()
            flash('User Created.', 'success')
            login_user(user, remember=True)
            return redirect(url_for('chat.home'))
    return render_template('auth/register.html', form=form)
