import os

from flask import current_app as app

from scratch.models import (
    Tender, Winner, save_tender, save_winner, set_notified, update_tender,
)

from scratch.scraper import (
    parse_tenders_list, parse_winners_list, parse_tender, parse_winner,
)
from scratch.utils import string_to_date
from scratch.mails import (
    send_tender_mail, send_winner_mail, send_update_mail, send_warning_mail,
)


def get_new_winners(request_cls):
    saved_winners = (
        Winner.query
        .with_entities(Winner.tender)
        .with_entities(Tender.reference)
        .all()
    )

    requested_html_winners = request_cls.request_winners_list()
    try:
        requested_winners = parse_winners_list(requested_html_winners)
    except Exception as e:
        send_warning_mail(e, 'parse_winners_list')
        return []

    new_winners = filter(
        lambda x: (x['reference'], ) not in saved_winners,
        requested_winners
    )

    if not new_winners:
        return []

    winners = []
    for new_winner in new_winners:
        html_data = request_cls.get_request(new_winner['url'])
        try:
            tender_fields, winner_fields = parse_winner(html_data)
        except Exception as e:
            send_warning_mail(e, 'parse_winner', new_winner['url'])
            return winners
        tender = save_winner(tender_fields, winner_fields)
        winners.append(tender.winner[0])

    return winners


def get_new_tenders(last_date, request_cls):
    last_references = (
        Tender.query
        .filter(Tender.published >= last_date)
        .with_entities(Tender.reference)
        .all()
    )

    requested_html_tenders = request_cls.request_tenders_list()
    try:
        extracted_tenders = parse_tenders_list(requested_html_tenders)
    except Exception as e:
        send_warning_mail(e, 'parse_tenders_list')
        return []

    new_tenders = filter(
        lambda x: (
            string_to_date(x['published']) >= last_date and
            (x['reference'], ) not in last_references
        ),
        extracted_tenders
    )

    if not new_tenders:
        return []

    tenders = []
    for new_tender in new_tenders:
        url = new_tender['url']
        html_data = request_cls.get_request(url)
        try:
            tender_fields = parse_tender(html_data)
        except Exception as e:
            send_warning_mail(e, 'parse_tender', url)
            return tenders
        tender_fields.update({'url': url})
        tender = save_tender(tender_fields)
        for document in tender_fields['documents']:
            save_document(document, str(tender.id), request_cls)
        tenders.append(tender)

    return tenders


def save_document(document, dirname, request_cls):
    doc = request_cls.request_document(document['download_url'])
    if doc:
        filename = document['name']
        path = os.path.join(app.config['FILES_DIR'], dirname)
        if not os.path.exists(path):
            os.makedirs(path)
        with open(os.path.join(path, filename), "wb") as doc_file:
            doc_file.write(doc)


def send_tenders_mail(tenders):
    for tender in tenders:
        subject = 'UNGM - New tender available'
        recipients = app.config.get('NOTIFY_EMAILS', [])
        sender = 'Eau De Web'
        if send_tender_mail(tender, subject, recipients, sender):
            set_notified(tender)


def send_winners_mail(winners):
    for winner in winners:
        subject = 'UNGM - New Contract Award'
        recipients = app.config.get('NOTIFY_EMAILS', [])
        sender = 'Eau De Web'
        if send_winner_mail(winner, subject, recipients, sender):
            set_notified(winner)


def scrap_favorites(request_cls):
    tenders = Tender.query.filter_by(favourite=True).all()

    changed_tenders = []
    for tender in tenders:
        html_data = request_cls.get_request(tender.url)
        try:
            tender_fields = parse_tender(html_data)
        except Exception as e:
            send_warning_mail(e, 'parse_tender', tender.url)

        attr_changes = {}
        for attr, value in [(k, v) for (k, v) in tender_fields.items()
                            if k != 'documents']:
            old_value = getattr(tender, attr)
            if value != old_value:
                attr_changes.update({attr: (old_value, value)})
                update_tender(tender, attr, value)

        new_docs = []
        received_docs = tender_fields['documents']
        saved_docs = [
            {'name': d.name, 'download_url': d.download_url}
            for d in tender.documents
        ]
        for document in received_docs:
            if document not in saved_docs:
                new_docs.append(document['name'])
                save_document(document, str(tender.id), request_cls)

        if attr_changes or new_docs:
            changed_tenders.append((tender, attr_changes, new_docs))

    return changed_tenders


def send_updates_mail(changed_tenders):
    for tender, changes, docs in changed_tenders:
        subject = 'UNGM - Tender Update'
        recipients = app.config.get('NOTIFY_EMAILS', [])
        sender = 'Eau De Web'
        send_update_mail(tender, changes, docs, subject, recipients, sender)
