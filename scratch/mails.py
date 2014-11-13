import smtplib
import os

from flask.ext.mail import Mail, Message
from flask import current_app as app, render_template

from scratch.models import set_notified


def send_tenders_mail(tenders, attachment, digest):
    subject = 'New tenders available' if digest else 'New tender available'
    recipients = app.config.get('NOTIFY_EMAILS', [])
    if digest:
        html = render_template('mails/new_tenders.html', tenders=tenders)
        if send_mail(subject, recipients, html, attachment):
            for tender in tenders:
                set_notified(tender)
    else:
        for tender in tenders:
            html = render_template('mails/new_tenders.html', tenders=[tender])
            if send_mail(subject, recipients, html, attachment,
                         tender_id=tender.id):
                set_notified(tender)


def send_winners_mail(winners, digest):
    subject = 'New contract award' if digest else 'New contract awards'
    recipients = app.config.get('NOTIFY_EMAILS', [])
    if digest:
        html = render_template('mails/new_winners.html', winners=winners)
        if send_mail(subject, recipients, html):
            for winner in winners:
                set_notified(winner)
    else:
        for winner in winners:
            html = render_template('mails/new_winners.html', winners=[winner])
            if send_mail(subject, recipients, html):
                set_notified(winner)


def send_updates_mail(changed_tenders, attachment, digest):
    subject = 'UNGM - Tender update'
    recipients = app.config.get('NOTIFY_EMAILS', [])
    if digest:
        html = render_template('mails/tender_update.html',
                               tenders=changed_tenders)
        send_mail(subject, recipients, html, attachment)
    else:
        for tender, changes, docs in changed_tenders:
            html = render_template(
                'mails/tender_update.html',
                tenders=[(tender, changes, docs)],
            ),
            send_mail(subject, recipients, html,
                      attachment=True, tender_id=tender.id, new_docs=docs)


def send_deadline_mail(tender, days_remained):
    subject = 'Deadline alert'
    recipients = app.config.get('NOTIFY_EMAILS', [])
    html = render_template(
        'mails/deadline_alert.html',
        tender=tender,
        days_remained=days_remained,
    )
    send_mail(subject, recipients, html)


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


def send_mail(subject, recipients, html, attachment=False, **kwargs):
    sender = 'Eau de Web <%s>' % app.config.get('MAIL_USERNAME')
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
