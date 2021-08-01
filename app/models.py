from flask import current_app
from flask_login import UserMixin
import jwt
from datetime import datetime

from app import db, login


@login.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()  # id 是 class User裡面的 id 欄位


# an example of many to many table
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id')),
                     )


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    avatar_img = db.Column(db.String(120), default="/static/images/avatar/unknown_user.jpeg", nullable=False)

    # connect to Post table
    # set relationship() in the "one" of one to many
    # backref() 是讓 post table 可以用 屬性 author 找到對應到 User table 的哪一筆資料
    posts = db.relationship('Post', backref=db.backref('author', lazy=True))

    # connect to follower table
    # User 自己連自己， 中間透過 followers table 連接 , i.e.
    # select * from User u1
    # join followers on u1.id = followers.follower_id
    # join User u2 on followers.followed_id = u2.id
    followed = db.relationship('User', secondary=followers,
                               primaryjoin=(followers.c.follower_id == id), # 被誰關注
                               secondaryjoin=(followers.c.followed_id == id), # 關注誰
                               backref=db.backref('followers', lazy=True),
                               lazy=True
                               )

    def __repr__(self):  # the content of print(User)
        return '<User %r>' % self.username

    def generate_reset_password_token(self):
        return jwt.encode({"id": self.id}, current_app.config['SECRET_KEY'], algorithm="HS256")

    @staticmethod
    def check_reset_password_token(token):
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            return User.query.filter_by(id=data['id']).first()
        except:
            return

    # add follow argv "user"
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    # remove follow argv "user"
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    # check whether is following argv "user"
    def is_following(self, user):
        return self.followed.count(user) > 0


# an example of one (User) to many (Post) table
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    # set ForeignKey() in the "many" of one to many
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                        nullable=False)  # 'user.id' as foreign key of post table, user會是class名稱的小寫，也可以改寫 __tablename__

    def __repr__(self):
        return '<Post {}>'.format((self.body))



