import smtplib
import os

from flask.ext.mail import Mail, Message
from flask import current_app as app, render_template


def attach(msg, tender_id):
    path = os.path.join(app.config['FILES_DIR'], str(tender_id))
    if not os.path.exists(path):
        return
    for file_name in os.listdir(path):
        document = open(os.path.join(path, file_name), 'rb')
        msg.attach(
            file_name.replace(' ', '_'),
            'application/unknown',
            document.read()
        )
        document.close()


def send_tender_mail(tender, subject, recipients, sender):
    msg = Message(
        subject=subject,
        recipients=recipients,
        html=render_template(
            'mails/single_tender.html',
            tender=tender,
        ),
        sender=sender,
    )
    attach(msg, tender.id)
    return send_mail(msg)


def send_winner_mail(winner, subject, recipients, sender):
    msg = Message(
        subject=subject,
        recipients=recipients,
        html=render_template(
            'mails/single_winner.html',
            winner=winner,
        ),
        sender=sender,
    )
    return send_mail(msg)


def send_mail(msg):
    mail = Mail(app)
    try:
        mail.send(msg)
        return True
    except smtplib.SMTPAuthenticationError:
        print 'Wrong username/password. ' + \
            'Please review their values in settings.py'
        return False
