from flask import render_template, url_for, redirect, request, send_from_directory, flash
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.utils import secure_filename

from app import app, bcrypt, db
from app.forms import *
from app.models import User, Post
from app.email import send_reset_password_mail

import os

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# 首頁
@app.route('/', methods=['POST', 'GET'])  # 表示首頁('IP:post/')會執行下面的function, methods列出允許的method, GET是預設開啟網頁，所以一定要列上
@login_required
def index():
    print('index')
    # return "<h1>Hello World!</h1>"
    name_length = len('Hello, ' + current_user.username)
    return render_template('index.html', length=name_length)


# 指定URL
@app.route('/test', methods=['POST', 'GET'])  # url = localhost:5000/test
@login_required
def test():
    # return "<h1>Hello World (Test)!</h1>"
    # return render_template('test.html')
    # return url_for('index') # url_for() 回傳index()所在的@app.route()路徑，i.e. '/'
    # return redirect(url_for('index')) # 轉跳到其他頁面
    if request.method == 'POST':
        if request.values['send'] == 'Send':
            title = 'Flask Tutorial for ' + request.values['user']
            return render_template('test.html', title=title, name=request.values['user'], user='')
    return render_template('test.html')


# 可變URL
@app.route('/<name>')  # url = localhost:5000/<name>
def your_name(name):
    # return "<h1>Hello " + name + "</h1>"
    file_name = name + '.html'
    return render_template(file_name)


##1, 3 可合併成以下
# @app.route('/')
# @app.route('/<name>') # 將網址設定成帶有變數功能
# def index(name=None):
#     if name==None:
#         return "<h1>Hello World!</h1>"
#     return "<h1>Hello " + name + "</h1>"

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='images/flask.ico')


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


@app.route('/contact_us', methods=['POST', 'GET'])
def contact_us():
    form = ContactUsForm()
    if form.validate_on_submit():
        body = form.text.data
        post = Post(body=body)
        current_user.posts.append(post)
        db.session.commit()
        flash('You have post a new content.', category='success')

    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, 2, False) # paginate() 製作分頁, 2是每頁兩筆資料, False不報錯
    return render_template('contact_us.html', form=form, posts=posts)


@app.route('/my_profile', methods=['POST', 'GET'])
def my_profile():
    n_followers = len(current_user.followers)
    n_followed = len(current_user.followed)
    return render_template('my_profile.html', n_followers=n_followers, n_followed=n_followed)


@app.route('/user_page/<username>')
@login_required
def user_page(username):
    user = User.query.filter_by(username=username).first()
    n_followers = len(user.followers)
    n_followed = len(user.followed)
    if user:
        return render_template('user_page.html', user=user, n_followers=n_followers, n_followed=n_followed)
    else:
        return '404'


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    n_followers = len(user.followers)
    n_followed = len(user.followed)
    if user:
        current_user.follow(user)
        db.session.commit()
        return render_template('user_page.html', user=user, n_followers=n_followers, n_followed=n_followed)
    else:
        return '404'


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    n_followers = len(user.followers)
    n_followed = len(user.followed)
    if user:
        current_user.unfollow(user)
        db.session.commit()
        return render_template('user_page.html', user=user, n_followers=n_followers, n_followed=n_followed)
    else:
        return '404'


@app.route('/upload_avatar', methods=['POST', 'GET'])
@login_required
def upload_avatar():
    form = UploadAvatarForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            f = form.avatar.data
            print(f.filename[-3])
            # if f.filename == '':
            #     flash('No Selected file', category='danger')
            #     return render_template('upload_avatar.html', form=form)
            if f:
                filename = secure_filename(f.filename)
                f.save(os.path.join(
                    'app', 'static', 'images/avatar', filename
                ))
                current_user.avatar_img = '/static/images/avatar/' + filename
                db.session.commit()
                return redirect(url_for('user_page', username=current_user.username))
        elif form.avatar.data.filename[-3] not in ['jpg', 'png', 'jpeg', 'gif']:
            flash('Image only', category='danger')
            return render_template('upload_avatar.html', form=form)
    return render_template('upload_avatar.html', form=form)

