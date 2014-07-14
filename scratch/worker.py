from scratch.scraper import parse_tender_list, parse_tender


def get_tender_list(start_date=None, end_date=None, cpv_codes=None):
    """
    Request a list of tenders with the specified filters.
    """
    # result = requests.get ...
    # return parse_tender_list(result.body)


def get_tender(url):
    """
    Request a tender details page. Handle details and downloads
    """
    # result = requests.get ...
    # tender = parse_tender(result.body)
    # tender = Tender(title=data['title'], ...)
    # return tender

