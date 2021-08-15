from flask import render_template, url_for, redirect, request, send_from_directory, flash
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.utils import secure_filename

from app import app, bcrypt, db
from app.forms import *
from app.models import User, Post

import os

from .view.auth import app_auth
app.register_blueprint(app_auth)

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

