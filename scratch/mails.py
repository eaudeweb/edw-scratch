from flask.ext.mail import Mail, Message

from server_requests import request_document


def send_email(subject, sender, recipients, html_body, tenders, public):
    from flask import current_app as app

    mail = Mail(app)
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = html_body
    for (index, tender) in tenders:
        for document in tender['documents']:
            attachement = request_document(document['download_url'], public)
            if attachement:
                msg.attach(
                    '%s.%s' % (index, document['name'].replace(' ', '_')),
                    'application/unknown',
                    attachement
                )
    mail.send(msg)
