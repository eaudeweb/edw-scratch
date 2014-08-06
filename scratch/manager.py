import pprint
from exceptions import AttributeError

from sqlalchemy import desc
from flask.ext.script import Manager
from flask import render_template, current_app
from scratch.models import db_manager, Tender, Winner, save_tender, save_winner
from scratch.server_requests import (
    request_tenders_list, request_winners_list, get_request,
)
from scratch.scraper import (
    parse_tenders_list, parse_winners_list, parse_tender, parse_winner
)
from scratch.mails import send_email
from scratch.utils import string_to_date, days_ago


TENDERS_ENDPOINT_URI = 'https://www.ungm.org/Public/Notice/'
WINNERS_ENDPOINT_URI = 'https://www.ungm.org/Public/ContractAward/'


scrap_manager = Manager()
add_manager = Manager()
worker_manager = Manager()
pp = pprint.PrettyPrinter(indent=4)


def create_manager(app):
    manager = Manager(app)
    manager.add_command('scrap', scrap_manager)
    manager.add_command('db', db_manager)
    manager.add_command('add', add_manager)
    manager.add_command('worker', worker_manager)

    return manager


@scrap_manager.command
def parse_tender_html(filename, public=False):
    data = get_request(TENDERS_ENDPOINT_URI + filename + '.html', public)
    pp.pprint(parse_tender(data))


@scrap_manager.command
def parse_winner_html(filename, public=False):
    data = get_request(WINNERS_ENDPOINT_URI + filename + '.html', public)
    tender_fields, winner_fields = parse_winner(data)
    tender_fields.update(winner_fields)
    pp.pprint(tender_fields)


@scrap_manager.command
def parse_tenders_list_html(public=False):
    data = request_tenders_list(public)
    pp.pprint(parse_tenders_list(data))


@scrap_manager.command
def parse_winners_list_html(public=False):
    data = request_winners_list(public)
    pp.pprint(parse_winners_list(data))


@add_manager.command
def add_tender(filename, public=False):
    html_data = get_request(TENDERS_ENDPOINT_URI + filename + '.html', public)
    tender = parse_tender(html_data)

    save_tender(tender)


@add_manager.command
def add_winner(filename, public=False):
    html_data = get_request(WINNERS_ENDPOINT_URI + filename + '.html', public)
    tender_fields, winner_fields = parse_winner(html_data)

    save_winner(tender_fields, winner_fields)


def _get_common_mail_fields(tender):
    return {
        'tender_id': tender['id'],
        'title': tender['title'],
        'organization': tender['organization'],
    }


def _get_tender_mail_fields(tender):
    fields = {
        'published': tender['published'],
        'deadline': tender['deadline'],
        'documents': tender['documents'],
    }
    fields.update(_get_common_mail_fields(tender))

    return fields


def _get_winner_mail_fields(tender, winner):
    fields = {
        'value': winner['value'],
    }
    fields.update(_get_common_mail_fields(tender))

    return fields


def _get_new_tenders(last_date, public):
    last_references = (
        Tender.query
        .filter(Tender.published >= last_date)
        .with_entities(Tender.reference)
        .all()
    )

    requested_html_tenders = request_tenders_list(public)
    extracted_tenders = parse_tenders_list(requested_html_tenders)

    return filter(
        lambda x: (
            string_to_date(x['published']) >= last_date and
            (x['reference'], ) not in last_references
        ),
        extracted_tenders
    )


def _get_new_winners(public):
    saved_winners = (
        Winner.query
        .with_entities(Winner.tender)
        .with_entities(Tender.reference)
        .all()
    )

    requested_html_winners = request_winners_list(public)
    requested_winners = parse_winners_list(requested_html_winners)

    return filter(
        lambda x: (x['reference'], ) not in saved_winners,
        requested_winners
    )


@worker_manager.option('-d', '--days', dest='days', default=30)
@worker_manager.option('-p', '--public', dest='public', default=False)
def update(days, public):

    try:
        last_date = (
            Tender.query
            .order_by(desc(Tender.published))
            .first()
            .published
        )
    except AttributeError:
        last_date = days_ago(int(days))

    new_tenders = _get_new_tenders(last_date, public)
    new_winners = _get_new_winners(public)

    if not new_tenders and not new_winners:
        return

    tenders = []
    for new_tender in new_tenders:
        html_data = get_request(new_tender['url'], public)
        tender_fields = parse_tender(html_data)
        tender_fields['id'] = save_tender(tender_fields)
        tenders.append(_get_tender_mail_fields(tender_fields))

    winners = []
    for new_winner in new_winners:
        html_data = get_request(new_winner['url'], public)
        tender_fields, winner_fields = parse_winner(html_data)
        tender_fields['id'] = save_winner(tender_fields, winner_fields)
        winners.append(_get_winner_mail_fields(tender_fields, winner_fields))

    recipients = current_app.config.get('NOTIFY_EMAILS', [])
    send_email(
        subject='New UNGM tenders available',
        sender='Eau De Web',
        recipients=recipients,
        html_body=render_template(
            'email.html',
            tenders=enumerate(tenders),
            winners=winners,
            tenders_size=len(tenders)
        ),
        tenders=enumerate(tenders),
        public=public
    )
