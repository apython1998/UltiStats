import string, os, tempfile
import datetime as dt
import logging
from flask import render_template, url_for, redirect, flash, request, \
    jsonify, current_app, send_file, abort
from app import db
from app.models import User
from app.main import bp
from app.main.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template("main/index.html")


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        newuser = User(username=form.username.data)
        newuser.set_password(form.password.data)
        db.session.add(newuser)
        db.session.commit()
        flash('You are now registered %s' % newuser.username)
        login_user(newuser)
        return redirect(url_for('main.login'))
    return render_template('main/register.html', title='Register', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return render_template('main/index.html')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return render_template('main/login.html', form=form)
        login_user(user, remember=True)
        flash('Login successful')
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('main/login.html', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
