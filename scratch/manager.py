import pprint
import urllib

from flask.ext.script import Manager
from scratch.server_requests import (
    get_request_class, PAYLOAD, TENDERS_ENDPOINT_URI, SEARCH_UNSPSCS_URI,
)
from scratch.models import (db_manager, last_update, save_tender, save_winner,
                            db)
from scratch.scraper import (
    parse_tenders_list, parse_winners_list, parse_tender, parse_winner,
    parse_UNSPSCs_list,
)
from scratch.worker import (get_new_tenders, get_new_winners, send_tenders_mail,
                            send_winners_mail, add_worker_log)
from scratch.utils import days_ago


TENDERS_ENDPOINT_URI = 'https://www.ungm.org/Public/Notice/'
WINNERS_ENDPOINT_URI = 'https://www.ungm.org/Public/ContractAward/'


scrap_manager = Manager()
add_manager = Manager()
worker_manager = Manager()
utils_manager = Manager()
pp = pprint.PrettyPrinter(indent=4)


def create_manager(app):
    manager = Manager(app)
    manager.add_command('scrap', scrap_manager)
    manager.add_command('db', db_manager)
    manager.add_command('add', add_manager)
    manager.add_command('worker', worker_manager)
    manager.add_command('utils', utils_manager)

    return manager


@db_manager.command
def init():
    db.create_all()


@scrap_manager.command
def parse_tender_html(filename, public=False):
    request_cls = get_request_class(public)
    data = request_cls.get_request(TENDERS_ENDPOINT_URI + filename)
    pp.pprint(parse_tender(data))


@scrap_manager.command
def parse_winner_html(filename, public=False):
    request_cls = get_request_class(public)
    data = request_cls.get_request(WINNERS_ENDPOINT_URI + filename)
    tender_fields, winner_fields = parse_winner(data)
    tender_fields.update(winner_fields)
    pp.pprint(tender_fields)


@scrap_manager.command
def parse_tenders_list_html(public=False):
    request_cls = get_request_class(public)
    data = request_cls.request_tenders_list()
    pp.pprint(parse_tenders_list(data))


@scrap_manager.command
def parse_winners_list_html(public=False):
    request_cls = get_request_class(public)
    data = request_cls.request_winners_list()
    pp.pprint(parse_winners_list(data))


@add_manager.command
def add_tender(filename, public=False):
    request_cls = get_request_class(public)
    html_data = request_cls.get_request(TENDERS_ENDPOINT_URI + filename)
    tender = parse_tender(html_data)

    save_tender(tender)


@add_manager.command
def add_winner(filename, public=False):
    request_cls = get_request_class(public)
    html_data = request_cls.get_request(WINNERS_ENDPOINT_URI + filename)
    tender_fields, winner_fields = parse_winner(html_data)

    save_winner(tender_fields, winner_fields)


@worker_manager.option('-d', '--days', dest='days', default=30)
@worker_manager.option('-p', '--public', dest='public', default=False)
def update(days, public):
    request_cls = get_request_class(public)
    last_date = last_update() or days_ago(days)

    new_tenders = get_new_tenders(last_date, request_cls)
    new_winners = get_new_winners(request_cls)

    send_tenders_mail(new_tenders, request_cls)
    send_winners_mail(new_winners)

    add_worker_log()


@utils_manager.option('-t', '--text', dest='text',
                      help='Text used to filter UNSPSCs.', required=True)
def search_unspscs(text):
    payload = PAYLOAD['unspsc']
    payload.update(filter=text)
    data = urllib.urlencode(payload)

    resp = get_request_class().post_request(
        TENDERS_ENDPOINT_URI, SEARCH_UNSPSCS_URI, data,
        content_type='application/x-www-form-urlencoded; charset=UTF-8')

    if resp:
        UNSPSCs = parse_UNSPSCs_list(resp)
        if not UNSPSCs:
            print 'Search returned no results.'
        for UNSPSC in UNSPSCs:
            print 'ID: {id}    NAME: {name}'.format(**UNSPSC)
    else:
        print 'POST request failed.'
