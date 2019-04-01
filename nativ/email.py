from flask import render_template, current_app
from threading import Thread
from flask_mail import Message
from nativ import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()



def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Boson] 重置密码',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))

def send_register_email(unComfiredUser):
    token = unComfiredUser.get_confirm_token()
    send_email('[Boson] 验证邮箱',
               sender=current_app.config['ADMINS'][0],
               recipients=[unComfiredUser.email],
               text_body=render_template('email/confirm_email.txt',
                                         user=unComfiredUser, token=token),
               html_body=render_template('email/confirm_email.html',
                                         user=unComfiredUser, token=token))
