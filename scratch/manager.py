import pprint

from flask.ext.script import Manager
from scratch.models import db_manager, save_tender, save_winner
from scratch.server_requests import (
    request_tenders_list, request_winners_list, get_request,
)
from scratch.scraper import (
    parse_tenders_list, parse_winners_list, parse_tender, parse_winner
)
from scratch.worker import (get_new_tenders, get_new_winners, send_tenders_mail,
                            send_winners_mail)


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
    data = get_request(TENDERS_ENDPOINT_URI + filename, public)
    pp.pprint(parse_tender(data))


@scrap_manager.command
def parse_winner_html(filename, public=False):
    data = get_request(WINNERS_ENDPOINT_URI + filename, public)
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
    html_data = get_request(TENDERS_ENDPOINT_URI + filename, public)
    tender = parse_tender(html_data)

    save_tender(tender)


@add_manager.command
def add_winner(filename, public=False):
    html_data = get_request(WINNERS_ENDPOINT_URI + filename, public)
    tender_fields, winner_fields = parse_winner(html_data)

    save_winner(tender_fields, winner_fields)



@worker_manager.option('-d', '--days', dest='days', default=30)
@worker_manager.option('-p', '--public', dest='public', default=False)
def update(days, public):

    new_tenders = get_new_tenders(days, public)
    new_winners = get_new_winners(public)

    send_tenders_mail(new_tenders, public)
    send_winners_mail(new_winners)
