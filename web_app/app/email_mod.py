import os
import smtplib, ssl
from email.message import EmailMessage
from typing import Text
from flask import render_template
from web_app.config2 import Config
#from web_app.app.templates.email import reset_password as reset_pass_html


def send_email(subject, sender, recipients, text_body, html_body):
    msg = EmailMessage()
    msg.set_content(text_body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipients
    msg.add_alternative(html_body, subtype='html')

    context=ssl.create_default_context()

    with smtplib.SMTP("smtp.googlemail.com", port=587) as smtp:
        smtp.starttls(context=context)
        smtp.login(msg["From"], "password")
        smtp.send_message(msg)
"""
def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(subject='[Flit] Reset your password',
    sender=Config.ADMINS[0],
    recipients=[user.email],
    text_body=render_template('email_folder/reset_password.txt', user=user, token=token),
    html_body=render_template('email_folder/reset_password.html', user=user, token=token))
"""

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Flit] Reset Your Password',
               sender=Config.ADMINS[0],
               recipients=[user.email],
               text_body=render_template('email_folder/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email_folder/reset_password.html',
                                         user=user, token=token))