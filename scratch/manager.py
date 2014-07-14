from flask.ext.script import Manager


scrap_manager = Manager()


def create_manager(app):
    manager = Manager(app)
    manager.add_command('scrap', scrap_manager)

    return manager


@scrap_manager.command
def parse_tender_html(filename):
    from scratch.scraper import parse_tender
    with open(filename, 'r') as fin:
        data = fin.read()

        print parse_tender(data)


@scrap_manager.command
def parse_tender_list_html(filename):
    from scratch.scraper import parse_tender_list
    with open(filename, 'r') as fin:
        data = fin.read()

        print parse_tender_list(data)


@scrap_manager.command
def parse_contract_html(filename):
    pass
