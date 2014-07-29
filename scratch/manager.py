import pprint

from sqlalchemy import desc
from flask.ext.script import Manager
from flask import render_template

from models import db, db_manager, Tender, Winner, TenderDocument
from scratch.server_requests import (
    request_tenders_list, request_winners_list, request,
)
from scratch.scraper import (
    parse_tenders_list, parse_winners_list, parse_tender, parse_winner
)
from scratch.mails import send_email
from utils import string_to_date, days_ago
from instance.settings import NOTIFY_EMAILS


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
    data = request(TENDERS_ENDPOINT_URI + filename + '.html', public)
    pp.pprint(parse_tender(data))


@scrap_manager.command
def parse_winner_html(filename, public=False):
    data = request(WINNERS_ENDPOINT_URI + filename + '.html', public)
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


def save_tender(tender):

    documents = tender.pop('documents')
    tender_entry = Tender(**tender)
    for document in documents:
        document_entry = TenderDocument(tender=tender_entry, **document)
        db.session.add(document_entry)
    db.session.add(tender_entry)
    db.session.commit()
    tender['documents'] = documents

    return tender_entry.id


@add_manager.command
def add_tender(filename, public=False):
    html_data = request(TENDERS_ENDPOINT_URI + filename + '.html', public)
    tender = parse_tender(html_data)

    save_tender(tender)


def save_winner(tender_fields, winner_fields):

    tender = Tender.query.filter_by(**tender_fields).first()
    if not tender:
        tender_entry = Tender(**tender_fields)
        db.session.add(tender_entry)
        db.session.commit()
    else:
        tender_entry = tender
    winner_entry = Winner(tender=tender_entry, **winner_fields)
    db.session.add(winner_entry)
    db.session.commit()

    return tender_entry.id


@add_manager.command
def add_winner(filename, public=False):
    html_data = request(WINNERS_ENDPOINT_URI + filename + '.html', public)
    tender_fields, winner_fields = parse_winner(html_data)

    save_winner(tender_fields, winner_fields)


def _get_tender_mail_fields(tender):
    return {
        'tender_id': tender['id'],
        'title': tender['title'],
        'organization': tender['organization'],
        'published': tender['published'],
        'deadline': tender['deadline'],
        'documents': tender['documents'],
    }


def _get_winner_mail_fields(tender, winner):
    return {
        'tender_id': tender['id'],
        'title': tender['title'],
        'organization': tender['organization'],
        'value': winner['value'],
    }


def _get_new_tenders(days, public):
    saved_tenders = (
        Tender.query
        .with_entities(Tender.reference, Tender.published)
        .order_by(desc(Tender.published))
    )

    if saved_tenders.count() != 0:
        newest_published_date = saved_tenders.first().published

        newest_references = (
            saved_tenders.filter_by(published=newest_published_date)
            .with_entities(Tender.reference)
            .all()
        )
    else:
        newest_published_date = days_ago(int(days))
        newest_references = []

    requested_html_tenders = request_tenders_list(public)
    requested_tenders = parse_tenders_list(requested_html_tenders)

    return filter(
        lambda x: (
            string_to_date(x['published']) >= newest_published_date and
            (x['reference'], ) not in newest_references
        ),
        requested_tenders
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

    new_tenders = _get_new_tenders(days, public)
    new_winners = _get_new_winners(public)

    if not new_tenders and not new_winners:
        return

    tenders = []
    for new_tender in new_tenders:
        html_data = request(new_tender['url'], public)
        tender_fields = parse_tender(html_data)
        tender_fields['id'] = save_tender(tender_fields)
        tenders.append(_get_tender_mail_fields(tender_fields))

    winners = []
    for new_winner in new_winners:
        html_data = request(new_winner['url'], public)
        tender_fields, winner_fields = parse_winner(html_data)
        tender_fields['id'] = save_winner(tender_fields, winner_fields)
        winners.append(_get_winner_mail_fields(tender_fields, winner_fields))

    send_email(
        subject='%s new tenders available' % len(new_tenders),
        sender='Eau De Web',
        recipients=NOTIFY_EMAILS,
        html_body=render_template(
            'email.html',
            tenders=enumerate(tenders),
            tenders_size=len(tenders)
        ),
        tenders=enumerate(tenders),
        public=public
    )
