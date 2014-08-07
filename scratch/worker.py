from flask import current_app as app

from scratch.models import Tender, Winner, save_tender, save_winner
from scratch.scraper import (
    parse_tenders_list, parse_winners_list, parse_tender, parse_winner
)
from scratch.utils import string_to_date
from scratch.mails import send_tender_mail, send_winner_mail


def get_new_winners(request_cls):
    saved_winners = (
        Winner.query
        .with_entities(Winner.tender)
        .with_entities(Tender.reference)
        .all()
    )

    requested_html_winners = request_cls.request_winners_list()
    requested_winners = parse_winners_list(requested_html_winners)

    new_winners = filter(
        lambda x: (x['reference'], ) not in saved_winners,
        requested_winners
    )

    return [] if not new_winners \
        else get_new_winners_details(new_winners, request_cls)


def get_new_winners_details(new_winners, request_cls):

    winners = []
    for new_winner in new_winners:
        html_data = request_cls.get_request(new_winner['url'])
        tender_fields, winner_fields = parse_winner(html_data)
        tender_fields['id'] = save_winner(tender_fields, winner_fields)
        tender_fields.update(winner_fields)
        winners.append(tender_fields)

    return winners


def get_new_tenders(last_date, request_cls):

    last_references = (
        Tender.query
        .filter(Tender.published >= last_date)
        .with_entities(Tender.reference)
        .all()
    )

    requested_html_tenders = request_cls.request_tenders_list()
    extracted_tenders = parse_tenders_list(requested_html_tenders)

    new_tenders = filter(
        lambda x: (
            string_to_date(x['published']) >= last_date and
            (x['reference'], ) not in last_references
        ),
        extracted_tenders
    )

    return [] if not new_tenders \
        else get_new_tenders_details(new_tenders, request_cls)


def get_new_tenders_details(new_tenders, request_cls):

    tenders = []
    for new_tender in new_tenders:
        html_data = request_cls.get_request(new_tender['url'])
        tender_fields = parse_tender(html_data)
        tender_fields['id'] = save_tender(tender_fields)
        tenders.append(tender_fields)

    return tenders


def send_tenders_mail(tenders, request_cls):

    for tender in tenders:
        subject = 'UNGM - New tender available'
        recipients = app.config.get('NOTIFY_EMAILS', [])
        sender = 'Eau De Web'
        send_tender_mail(tender, subject, recipients, sender, request_cls)


def send_winners_mail(winners):

    for winner in winners:
        subject = 'UNGM - New Contract Award'
        recipients = app.config.get('NOTIFY_EMAILS', [])
        sender = 'Eau De Web'
        send_winner_mail(winner, subject, recipients, sender)
