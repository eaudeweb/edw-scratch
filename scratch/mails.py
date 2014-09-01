import smtplib
import os

from flask.ext.mail import Mail, Message
from flask import current_app as app, render_template

from scratch.models import set_notified


def send_tenders_mail(tenders, attachment, digest):
    subject = 'New tenders available' if digest else 'New tender available'
    recipients = app.config.get('NOTIFY_EMAILS', [])
    sender = 'Eau De Web'
    if digest:
        html = render_template('mails/new_tenders.html', tenders=tenders)
        if send_mail(subject, recipients, html, sender, attachment):
            for tender in tenders:
                set_notified(tender)
    else:
        for tender in tenders:
            html = render_template('mails/new_tenders.html', tenders=[tender])
            if send_mail(subject, recipients, html, sender, attachment,
                         tender_id=tender.id):
                set_notified(tender)


def send_winners_mail(winners, digest):
    subject = 'New contract award' if digest else 'New contract awards'
    recipients = app.config.get('NOTIFY_EMAILS', [])
    sender = 'Eau De Web'
    if digest:
        html = render_template('mails/new_winners.html', winners=winners)
        if send_mail(subject, recipients, html, sender):
            for winner in winners:
                set_notified(winners)
    else:
        for winner in winners:
            html = render_template('mails/new_winner.html', winners=[winner])
            if send_mail(subject, recipients, html, sender):
                set_notified(winner)


def send_updates_mail(changed_tenders):
    subject = 'UNGM - Tender Update'
    recipients = app.config.get('NOTIFY_EMAILS', [])
    sender = 'Eau De Web'
    for tender, changes, docs in changed_tenders:
        html = render_template(
            'mails/tender_update.html',
            tender=tender,
            changes=changes,
            documents=True if docs else False
        ),
        send_mail(subject, recipients, html, sender,
                  attachment=True, tender_id=tender.id, new_docs=docs)


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
