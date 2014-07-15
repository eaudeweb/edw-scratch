from bs4 import BeautifulSoup
from datetime import datetime


CSS_ROW_LIST_NAME = 'tableRow dataRow'
CSS_ROW_DETAIL_NAME = 'reportRow'
ENDPOINT_URI = 'https://www.ungm.org'
DOWNLOAD_PATH = '/UNUser/Documents/DownloadPublicDocument?docId='


def string_to_date(date):
    return datetime.strptime(date, '%d-%b-%Y').date()


def parse_tender(html):
    """ Parse a tender HTML and return a dictionary with information such
     as: title, description, published etc
    """

    soup = BeautifulSoup(html)
    details = soup.find_all('div', CSS_ROW_DETAIL_NAME)
    documents = soup.find_all('div', 'docslist')[0].find_all('div', 'filterDiv')

    tender = {
        'title': details[2].span.string,
        'organization': details[3].span.string,
        'reference': details[4].span.string,
        'published': string_to_date(details[5].span.string),
        'deadline': string_to_date(details[6].span.string.split(' ')[0]),
        'documents': [
            {
                'name': document.span.string,
                'download_url': (
                    ENDPOINT_URI + DOWNLOAD_PATH + document['data-documentid']
                )
            }
            for document in documents
        ]
    }

    return tender


def parse_tender_list(html):
    """ Parse a list of tenders and return a list of URLs.
    """

    soup = BeautifulSoup(html)
    tenders = soup.find_all('div', CSS_ROW_LIST_NAME)

    tenders_list = [
        ENDPOINT_URI + tender.contents[3].a['href'] + '.html'
        for tender in tenders
    ]

    return tenders_list


def parse_award(html):
    """ Parse a contract award HTML
    """
    return {}


def parse_winners_list(html):
    """Parse a list of contract awards and return a list of URLs
    """

    soup = BeautifulSoup(html)
    winners = soup.find_all('div', CSS_ROW_LIST_NAME)
    winners_list = [
        ENDPOINT_URI + winner.contents[1].a['href'] + '.html'
        for winner in winners
    ]

    return winners_list
