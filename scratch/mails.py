from flask.ext.mail import Mail, Message


def send_email(subject, sender, recipients, html_body):
    from flask import current_app as app

    mail = Mail(app)
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = html_body
    mail.send(msg)