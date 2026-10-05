from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from .extensions import db
from .forms import ActionForm, LoginForm, RegisterForm
from .models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('tracker.dashboard'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data.lower())
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            form.email.errors.append('An account with this email already exists.')
        else:
            login_user(user)
            flash('Your account is ready. Let’s track your first application!', 'success')
            return redirect(url_for('tracker.dashboard'))
    return render_template('auth.html', form=form, registering=True)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('tracker.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).where(User.email == form.email.data.lower()))
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('tracker.dashboard'))
        flash('Email or password is incorrect.', 'danger')
    return render_template('auth.html', form=form, registering=False)


@bp.post('/logout')
@login_required
def logout():
    form = ActionForm()
    if form.validate_on_submit():
        logout_user()
    return redirect(url_for('auth.login'))
