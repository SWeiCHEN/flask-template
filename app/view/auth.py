from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import login_user, login_required, current_user, logout_user

from app import app, bcrypt, db
from app.forms import SignUpForm, SignInForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.email import send_reset_password_mail

app_auth = Blueprint('app_auth', __name__, template_folder='../templates/auth')


@app_auth.route('/app_auth')
def test():
    return "test"


@app.route('/Sign_up', methods=['POST', 'GET'])
def sign_up():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = SignUpForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = bcrypt.generate_password_hash(form.password.data)  # encrypt
        # print(username, email, password)

        # write account information to database
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Congrats, sign up successfully', category='success')  # backend send message to frontend
        return redirect(url_for('sign_in'))
    else:
        print(form.errors.items())
    return render_template('Sign_up.html', form=form)


@app.route('/Sign_in', methods=['POST', 'GET'])
def sign_in():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = SignInForm()
    if request.method == 'POST':  # flask-bootstrap 好像會自動判斷
        # print('inputed account information')
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            remember = form.remember.data

            user = User.query.filter_by(username=username).first()
            if user and bcrypt.check_password_hash(user.password, password):
                # User exists and password matched
                login_user(user, remember=remember)
                flash('Log in successfully', category='info')
                if request.args.get('next'):  # 被強制轉跳到Login page時，URL會有一個next參數，紀錄user原本想去哪頁
                    next_page = request.args.get('next')
                    return redirect(next_page)
                return redirect(url_for('index'))
            flash('User not exists or password not match', category='danger')  # 不明說是帳號不存在還是密碼錯誤，避免有心人士暴力破解
    return render_template('Sign_in.html', form=form)


@app.route('/Sign_out')
@login_required
def sign_out():
    logout_user()
    return redirect(url_for("sign_in"))


@app.route('/forgot_password', methods=['POST', 'GET'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        token = user.generate_reset_password_token()
        send_reset_password_mail(user, token)
        flash('Password reset request mail is sent, please check your mailbox', category='info')
    return render_template('forgot_password.html', form=form)


@app.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.check_reset_password_token(token)
        if user:
            user.password = bcrypt.generate_password_hash(form.password.data)
            db.session.commit()
            flash('Your password reset is done', category='info')
            return redirect(url_for('sign_in'))
        else:
            flash('The user is not exist', category='info')
            redirect(url_for('sign_in'))
    return render_template('reset_password.html', form=form)
