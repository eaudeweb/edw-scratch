import smtplib

from flask.ext.mail import Mail, Message
from flask import current_app as app, render_template


def attach(msg, documents, request_cls):
    for document in documents:
        attachement = request_cls.request_document(document['download_url'])
        if attachement:
            msg.attach(
                document['name'].replace(' ', '_'),
                'application/unknown',
                attachement
            )


def send_tender_mail(tender, subject, recipients, sender, request_cls):
    msg = Message(
        subject=subject,
        recipients=recipients,
        html=render_template(
            'mails/single_tender.html',
            tender=tender,
        ),
        sender=sender,
    )
    attach(msg, tender['documents'], request_cls)
    send_mail(msg)


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
    send_mail(msg)


def send_mail(msg):
    mail = Mail(app)
    try:
        mail.send(msg)
    except smtplib.SMTPAuthenticationError:
        print 'Wrong username/password. ' + \
            'Please review their values in settings.py'
