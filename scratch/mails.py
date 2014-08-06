import smtplib

from flask.ext.mail import Mail, Message
from flask import current_app as app

from server_requests import request_document
from instance.settings import NOTIFY_EMAILS


def attach(msg, documents, public, index=None):
    index = '' if index is None else '%s.' % index
    for document in documents:
        attachement = request_document(document['download_url'], public)
        if attachement:
            msg.attach(
                index + '%s' % document['name'].replace(' ', '_'),
                'application/unknown',
                attachement
            )


def send_mail(subject, html_body, public, tenders=None, sender='Eau De Web',
              recipients=NOTIFY_EMAILS):

    msg = Message(
        subject=subject,
        recipients=recipients,
        html=html_body,
        sender=sender,
    )
    if not tenders:
        pass
    elif len(tenders) == 1:
        tender = tenders.pop()
        attach(msg, tender['documents'], public)
    elif len(tenders) > 1:
        for (index, tender) in enumerate(tenders):
            attach(msg, tender['documents'], public, index)

    mail = Mail(app)
    try:
        mail.send(msg)
    except smtplib.SMTPAuthenticationError:
        print 'Wrong username/password. ' + \
            'Please review their values in settings.py'
