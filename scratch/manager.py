import pprint

from flask.ext.script import Manager


scrap_manager = Manager()
pp = pprint.PrettyPrinter(indent=4)


def create_manager(app):
    manager = Manager(app)
    manager.add_command('scrap', scrap_manager)

    return manager


@scrap_manager.command
def parse_tender_html(filename):
    from scratch.scraper import parse_tender
    with open(filename, 'r') as fin:
        data = fin.read()

        pp.pprint(parse_tender(data))


@scrap_manager.command
def parse_tender_list_html(filename):
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
