import smtplib
import os

from flask.ext.mail import Mail, Message
from flask import current_app as app


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


def send_mail(subject, recipients, html, sender, attachment=False, **kwargs):
    message = Message(subject=subject, recipients=recipients, html=html,
                      sender=sender)
    if attachment:
        attach(message, **kwargs)
    mail = Mail(app)
    try:
        mail.send(message)
        return True
    except smtplib.SMTPAuthenticationError:
        print 'Wrong username/password. ' + \
            'Please review their values in settings.py'
        return False
