from exceptions import AttributeError

from sqlalchemy import desc
from flask import current_app as app

from scratch.models import Tender, Winner, save_tender, save_winner
from scratch.server_requests import (
    request_tenders_list, request_winners_list, get_request,
)
from scratch.scraper import (
    parse_tenders_list, parse_winners_list, parse_tender, parse_winner
)
from scratch.utils import string_to_date, days_ago
from scratch.mails import send_tender_mail, send_winner_mail


def get_new_winners(public):
    saved_winners = (
        Winner.query
        .with_entities(Winner.tender)
        .with_entities(Tender.reference)
        .all()
    )

    requested_html_winners = request_winners_list(public)
    requested_winners = parse_winners_list(requested_html_winners)

    new_winners = filter(
        lambda x: (x['reference'], ) not in saved_winners,
        requested_winners
    )

    return [] if not new_winners else get_new_winners_details(new_winners, public)


def get_new_winners_details(new_winners, public):

    winners = []
    for new_winner in new_winners:
        html_data = get_request(new_winner['url'], public)
        tender_fields, winner_fields = parse_winner(html_data)
        tender_fields['id'] = save_winner(tender_fields, winner_fields)
        tender_fields.update(winner_fields)
        winners.append(tender_fields)

    return winners


def get_new_tenders(days, public):
    try:
        last_date = (
            Tender.query
            .order_by(desc(Tender.published))
            .first()
            .published
        )
    except AttributeError:
        last_date = days_ago(int(days))

    last_references = (
        Tender.query
        .filter(Tender.published >= last_date)
        .with_entities(Tender.reference)
        .all()
    )

    requested_html_tenders = request_tenders_list(public)
    extracted_tenders = parse_tenders_list(requested_html_tenders)

    new_tenders = filter(
        lambda x: (
            string_to_date(x['published']) >= last_date and
            (x['reference'], ) not in last_references
        ),
        extracted_tenders
    )

    return [] if not new_tenders else get_new_tenders_details(new_tenders, public)


def get_new_tenders_details(new_tenders, public):
    if not new_tenders:
        return []

    tenders = []
    for new_tender in new_tenders:
        html_data = get_request(new_tender['url'], public)
        tender_fields = parse_tender(html_data)
        tender_fields['id'] = save_tender(tender_fields)
        tenders.append(tender_fields)

    return tenders


def send_tenders_mail(tenders, public):

    for tender in tenders:
        subject = 'UNGM - New tender available'
        recipients = app.config.get('NOTIFY_EMAILS', [])
        sender = 'Eau De Web'
        send_tender_mail(tender, subject, recipients, sender, public)


def send_winners_mail(winners):

    for winner in winners:
        subject = 'UNGM - New Contract Award'
        recipients = app.config.get('NOTIFY_EMAILS', [])
        sender = 'Eau De Web'
        send_winner_mail(winner, subject, recipients, sender)
