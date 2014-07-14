from bs4 import BeautifulSoup
from datetime import datetime


CSS_ROW_CLASS_NAME = 'tableRow dataRow'
ENDPOINT_URI = 'https://www.ungm.org'


def string_to_date(date):
    return datetime.strptime(date, '%d-%b-%Y').date()


def parse_tender(html):
    """ Parse a tender HTML and return a dictionary with information such
     as: title, description, published etc
    """


def parse_award(html):
    """ Parse a contract award HTML
    """
    return {}


def parse_tender_list(html):
    """ Parse a list of tenders and return a list of uris.
    """

    soup = BeautifulSoup(html)
    rows = soup.find_all('div', CSS_ROW_CLASS_NAME)
    tender_list = []

    for row in rows:
        href = row.contents[3].a['href']
        url = ENDPOINT_URI + unicode(href) + '.html'
        tender_list.append(url)

    return tender_list
