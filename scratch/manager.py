import pprint

from sqlalchemy import desc
from flask.ext.script import Manager

from models import db, db_manager, Tender, Winner, TenderDocument
from scratch.requests import request_tenders
from scratch.scraper import parse_tenders_list
from utils import string_to_date


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
def parse_tender_html(filename):
    from scratch.scraper import parse_tender
    with open(filename, 'r') as fin:
        data = fin.read()

        pp.pprint(parse_tender(data))


@scrap_manager.command
def parse_tenders_list_html(filename):
    from scratch.scraper import parse_tenders_list
    with open(filename, 'r') as fin:
        data = fin.read()

        pp.pprint(parse_tenders_list(data))


@scrap_manager.command
def parse_winners_list_html(filename):
    from scratch.scraper import parse_winners_list
    with open(filename, 'r') as fin:
        data = fin.read()

        pp.pprint(parse_winners_list(data))


@scrap_manager.command
def parse_winner_html(filename):
    from scratch.scraper import parse_winner
    with open(filename, 'r') as fin:
        data = fin.read()

        tender_fields, winner_fields = parse_winner(data)
        pp.pprint(tender_fields.update(winner_fields))


def add_tender_from_html(html):
    from scratch.scraper import parse_tender

    tender = parse_tender(html)
    documents = tender.pop('documents')
    tender_entry = Tender(**tender)
    for document in documents:
        document_entry = TenderDocument(tender=tender_entry, **document)
        db.session.add(document_entry)
    db.session.add(tender_entry)
    db.session.commit()


@add_manager.command
def add_tender(filename):
    with open(filename, 'r') as fin:
        html = fin.read()
    add_tender_from_html(html)


def add_winner_from_html(html):
    from scratch.scraper import parse_winner

    tender_fields, winner_fields = parse_winner(html)
    tender = Tender.query.filter_by(**tender_fields).first()
    if not tender:
        tender_entry = Tender(**tender_fields)
        db.session.add(tender_entry)
        db.session.commit()
    winner_entry = Winner(tender=tender_entry, **winner_fields)
    db.session.add(winner_entry)
    db.session.commit()


@add_manager.command
def add_winner(filename):
    with open(filename, 'r') as fin:
        html = fin.read()
    add_winner_from_html(html)


@worker_manager.command
def update():
    tenders = (
        Tender.query
        .with_entities(Tender.reference, Tender.published)
        .order_by(desc(Tender.published))
    )

    newest_published_date = tenders.first().published

    newest_references = (
        tenders.filter_by(published=newest_published_date)
        .with_entities(Tender.reference)
        .all()
    )

    html_tenders = request_tenders()
    tenders = parse_tenders_list(html_tenders)
    new_tenders = filter(
        lambda x: (
            string_to_date(x['published']) >= newest_published_date and
            (x['reference'], ) not in newest_references
        ),
        tenders
    )
    pp.pprint(new_tenders)
