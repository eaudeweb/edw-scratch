import smtplib
import os

from flask.ext.mail import Mail, Message
from flask import current_app as app, render_template


def attach(msg, tender_id, new_docs=None):
    path = os.path.join(app.config['FILES_DIR'], str(tender_id))
    if not os.path.exists(path):
        return
    for file_name in os.listdir(path):
        if new_docs is None or file_name in new_docs:
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


def send_update_mail(tender, changes, documents, subject, recipients, sender):
    msg = Message(
        subject=subject,
        recipients=recipients,
        html=render_template(
            'mails/tender_update.html',
            tender=tender,
            changes=changes,
            documents=True if documents else False
        ),
        sender=sender
    )
    attach(msg, tender.id, documents)

    return send_mail(msg)


def send_warning_mail(e, func_name, url=None):
    msg = Message(
        subject='Error while parsing',
        recipients=app.config['DEVELOPERS_EMAILS'],
        html=render_template(
            'mails/warning_mail.html',
            url=url,
            func_name=func_name,
            exception_type=type(e),
            exception_message=e.message,
        ),
        sender='Eau De Web'
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
