from flask import current_app, render_template
from flask_mail import Message
from threading import Thread

from app import mail, app


def send_async_mail(app, msg):
    with app.app_context():
        mail.send(msg)


def send_reset_password_mail(user, token):
    msg = Message("[Flask App] Reset Your Password",
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[user.email],
                  html=render_template('auth/reset_password_mail.html', user=user, token=token))
    # mail.send(msg)
    # send email by threading to make the web shows fast
    Thread(target=send_async_mail, args=(app, msg, )).start()
