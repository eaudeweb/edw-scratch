# coding=utf-8
import os
import json
from bs4 import BeautifulSoup
from datetime import date, timedelta

from utils import string_to_date, string_to_datetime, to_unicode, get_local_gmt

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
json_unspsc_codes = os.path.join(BASE_DIR, 'UNSPSC_codes_software.json')
CSS_ROW_LIST_NAME = 'tableRow dataRow'
CSS_ROW_DETAIL_NAME = 'reportRow'
CSS_DESCRIPTION = 'raw clear'
ENDPOINT_URI = 'https://www.ungm.org'
DOWNLOAD_PATH = '/UNUser/Documents/DownloadPublicDocument?docId='


def parse_tender(html):
    """ Parse a tender HTML and return a dictionary with information such
     as: title, description, published etc
    """

    soup = BeautifulSoup(html)
    details = soup.find_all('div', CSS_ROW_DETAIL_NAME)
    documents = soup.find_all('div', 'docslist')[0].find_all('div', 'filterDiv')
    description = soup.find_all('div', CSS_DESCRIPTION)
    unspsc_tree = soup.find_all('div', {'class': 'unspscTree'})[0]
    nodes = unspsc_tree.findAll('span', {'class': 'nodeName'})
    scraped_nodes = [node.text for node in nodes]
    with open(json_unspsc_codes, 'rb') as fp:
        codes = json.load(fp)
    unspsc_codes = [code['id']
                    for code in codes
                    if code['name'] in scraped_nodes]

    tender = {
        'source': 'UNGM',
        'notice_type': to_unicode(details[0].span.string),
        'title': to_unicode(details[2].span.string),
        'organization': to_unicode(details[3].span.string),
        'reference': to_unicode(details[4].span.string),
        'published': string_to_date(details[5].span.string) or date.today(),
        'deadline': string_to_datetime(details[6].span.string),
        'description': to_unicode(str(description[0])),
        'unspsc_codes': ', '.join(unspsc_codes),
        'documents': [
            {
                'name': to_unicode(document.span.string),
                'download_url': (
                    ENDPOINT_URI + DOWNLOAD_PATH + document['data-documentid']
                )
            }
            for document in documents
        ]
    }
    gmt = details[7].span.string.split('GMT')[1].split(')')[0]
    if gmt:
        tender['deadline'] -= timedelta(hours=float(gmt[1:]))
        tender['deadline'] += timedelta(hours=get_local_gmt())

    return tender


def parse_tenders_list(html):
    """ Parse a list of tenders and return a list of tenders
    Example: [{reference: ... , url: ...}, ...]
    """

    soup = BeautifulSoup(html)
    tenders = soup.find_all('div', CSS_ROW_LIST_NAME)

    tenders_list = [
        {
            'published': tender.contents[7].span.string or date.today(),
            'reference': tender.contents[13].span.string,
            'url': ENDPOINT_URI + tender.contents[3].a['href']
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
        'source': 'UNGM',
        'title': to_unicode(details[0].span.string),
        'organization': to_unicode(details[1].span.string),
        'reference': to_unicode(details[2].span.string),
        'description': to_unicode(str(description[0])),
    }
    winner_fields = {
        'award_date': string_to_date(details[3].span.string) or date.today(),
        'vendor': to_unicode(details[4].span.string),
        'value': float(details[5].span.string) if details[5].span.string
        else None
    }
    if winner_fields['value']:
        winner_fields['currency'] = 'USD'

    return tender_fields, winner_fields


def parse_winners_list(html):
    """Parse a list of contract awards and return a list winners
    Example: [{reference: ... , url: ...}, ...]
    """

    soup = BeautifulSoup(html)
    winners = soup.find_all('div', CSS_ROW_LIST_NAME)

    winners_list = [
        {
            'reference': winner.contents[7].span.string,
            'url': ENDPOINT_URI + winner.contents[1].a['href']
        }
        for winner in winners
    ]

    return winners_list


def parse_UNSPSCs_list(html):
    """Parse html containing UNSPSCs and return a list of dictionaries
    containing UNSPSC id and name.
    """
    soup = BeautifulSoup(html)
    nodes = soup.find_all('span', 'nodeName')
    UNSPSCs = []
    for node in nodes:
        if node.find_previous_sibling():
            UNSPSCs.append({
                'id': node.get('data-nodeid'),
                'name': node.text,
            })
    return UNSPSCs
