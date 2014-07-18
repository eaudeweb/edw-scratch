from bs4 import BeautifulSoup
from datetime import datetime, date


CSS_ROW_LIST_NAME = 'tableRow dataRow'
CSS_ROW_DETAIL_NAME = 'reportRow'
CSS_DESCRIPTION = 'raw clear'
ENDPOINT_URI = 'https://www.ungm.org'
DOWNLOAD_PATH = '/UNUser/Documents/DownloadPublicDocument?docId='


def string_to_date(string_date):
    if string_date:
        return datetime.strptime(string_date, '%d-%b-%Y').date()
    return None


def string_to_datetime(string_date):
    if string_date:
        return datetime.strptime(string_date, '%d-%b-%Y %H:%M')
    return None


def parse_tender(html):
    """ Parse a tender HTML and return a dictionary with information such
     as: title, description, published etc
    """

    soup = BeautifulSoup(html)
    details = soup.find_all('div', CSS_ROW_DETAIL_NAME)
    documents = soup.find_all('div', 'docslist')[0].find_all('div', 'filterDiv')
    description = soup.find_all('div', CSS_DESCRIPTION)
    tender = {
        'title': details[2].span.string or None,
        'organization': details[3].span.string or None,
        'reference': details[4].span.string or None,
        'published': string_to_date(details[5].span.string) or date.today(),
        'deadline': string_to_datetime(details[6].span.string),
        'description': str(description[0]),
        'documents': [
            {
                'name': document.span.string or None,
                'download_url': (
                    ENDPOINT_URI + DOWNLOAD_PATH + document['data-documentid']
                )
            }
            for document in documents
        ]
    }

    return tender


def parse_tenders_list(html):
    """ Parse a list of tenders and return a list of tenders
    Example: [{reference: ... , url: ...}, ...]
    """

    soup = BeautifulSoup(html)
    tenders = soup.find_all('div', CSS_ROW_LIST_NAME)

    tenders_list = [
        {
            'reference': tender.contents[13].span.string or None,
            'url': ENDPOINT_URI + tender.contents[3].a['href'] + '.html'
        }
        for tender in tenders
    ]

    return tenders_list


def parse_winner(html):
    """ Parse a contract award HTML and return a dictionary with information
     such as: title, reference, vendor etc
    """

    soup = BeautifulSoup(html)
    details = soup.find_all('div', CSS_ROW_DETAIL_NAME)
    description = soup.find_all('div', CSS_DESCRIPTION)
    tender_fields = {
        'title': details[0].span.string or None,
        'organization': details[1].span.string or None,
        'reference': details[2].span.string or None,
        'description': str(description[0]) or None,
    }
    winner_fields = {
        'award_date': string_to_date(details[3].span.string) or date.today(),
        'vendor': details[4].span.string or None,
        'value': float(details[5].span.string) or None
    }

    return tender_fields, winner_fields


def parse_winners_list(html):
    """Parse a list of contract awards and return a list winners
    Example: [{reference: ... , url: ...}, ...]
    """

    soup = BeautifulSoup(html)
    winners = soup.find_all('div', CSS_ROW_LIST_NAME)

    winners_list = [
        {
            'reference': winner.contents[7].span.string or None,
            'url': ENDPOINT_URI + winner.contents[1].a['href'] + '.html'

        }
        for winner in winners
    ]

    return winners_list
