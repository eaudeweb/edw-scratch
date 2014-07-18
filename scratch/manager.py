import pprint

from flask.ext.script import Manager

from models import db, db_manager, Tender, TenderDocument


scrap_manager = Manager()
add_manager = Manager()
pp = pprint.PrettyPrinter(indent=4)


def create_manager(app):
    manager = Manager(app)
    manager.add_command('scrap', scrap_manager)
    manager.add_command('db', db_manager)
    manager.add_command('add', add_manager)

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

        pp.pprint(parse_winner(data))


def add_tenders_from_html(html):
    from scratch.scraper import parse_tender
    tender = parse_tender(html)
    tender_entry = Tender(
        reference=tender['reference'],
        title=tender['title'],
        organization=tender['organization'],
        published=tender['published'],
        deadline=tender['deadline'],
    )
    for document in tender['documents']:
        document_entry = TenderDocument(
            name=document['name'],
            download_url=document['download_url'],
            tender=tender_entry,
        )
        db.session.add(document_entry)
    db.session.add(tender_entry)
    db.session.commit()


@add_manager.command
def add_tenders(filename):
    with open(filename, 'r') as fin:
        html = fin.read()
    add_tenders_from_html(html)
