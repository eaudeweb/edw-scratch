# coding=utf-8
import os
import re
import json
from bs4 import BeautifulSoup
from datetime import date, timedelta

from utils import string_to_date, string_to_datetime, to_unicode, get_local_gmt

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
json_unspsc_codes = os.path.join(BASE_DIR, 'UNSPSC_codes_software.json')
CSS_ROW_LIST_NAME = 'tableRow dataRow'
CSS_TITLE = 'Title'
CSS_LIST_TITLE = 'tableCell resultTitle'
CSS_ORGANIZATION = 'AgencyId'
CSS_REFERENCE = 'Reference'
CSS_AWARD_DATE = 'AwardDate'
CSS_VALUE = 'ContractValue'
CSS_VENDOR_LIST = 'contractAwardVendorsContainer'
CSS_ROW_DETAIL_NAME = 'reportRow'
CSS_DESCRIPTION = 'raw clear'
CSS_NOTICE_TYPE = 'NoticeType'
CSS_PUBLISHED = 'DatePublished'
CSS_DEADLINE = 'Deadline'
CSS_GMT = 'Timezone'
ENDPOINT_URI = 'https://www.ungm.org'
DOWNLOAD_PATH = '/UNUser/Documents/DownloadPublicDocument?docId='


def find_by_label(soup, label):
    return soup.find('label', attrs={'for': label}).next_sibling.next_sibling

def find_by_class(soup, class_value, element_type="span", text_return=False):
    try:
        result = soup.find_all(element_type, {"class": class_value })
        if text_return:
            result = result[0].text.strip()
        return result
    except IndexError:
        return None

def parse_tender(html):
    """ Parse a tender HTML and return a dictionary with information such
     as: title, description, published etc
    """
    soup = BeautifulSoup(html, 'html.parser')

    documents = find_by_class(soup, "lnkShowDocument", "a")
    description = find_by_class(soup, "ungm-list-item ungm-background", "div")
    description = description[1].text.strip().lstrip('Description')
    nodes = find_by_class(soup, "nodeName", "span")
    scraped_nodes =  [parent.find_all("span")[0].text for parent in nodes[1:]]
    with open(json_unspsc_codes, 'rb') as fp:
        codes = json.load(fp)
    unspsc_codes = [
        code['id'] for code in codes
        if code['id_ungm'] in scraped_nodes
    ]
    notice_type = find_by_class(soup, "status-tag", "span", True)
    title = find_by_class(soup, "title", "span", True)
    organization = find_by_class(soup, "highlighted", "span", True)

    reference = soup.find('span', text = re.compile('Reference:')).next_sibling.next_sibling.text
    published = soup.find('span', text = re.compile('Published on:')).next_sibling.next_sibling.text
    deadline = soup.find('span', text = re.compile('Deadline on:')).next_sibling.next_sibling.text

    tender = {
        'source': 'UNGM',
        'notice_type': notice_type,
        'title': title,
        'organization': organization,
        'reference': reference,
        'published': string_to_date(published) or date.today(),
        'deadline': string_to_datetime(deadline[:17]),
        'description': description,
        'unspsc_codes': ', '.join(unspsc_codes),
        'documents': [
            {
                'name': document.text.strip(),
                'download_url': ENDPOINT_URI + documents[0]['href']
            }
            for document in documents
        ],
    }

    gmt = deadline
    gmt = gmt[gmt.find("GMT")+4:gmt.find(")")]
    if gmt:
        tender['deadline'] -= timedelta(hours=float(gmt))
        tender['deadline'] += timedelta(hours=get_local_gmt())

    return tender


def parse_tenders_list(html):
    """ Parse a list of tenders and return a list of tenders
    Example: [{reference: ... , url: ...}, ...]
    """

    soup = BeautifulSoup(html, 'html.parser')
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

    soup = BeautifulSoup(html, 'html.parser')
    description = soup.find_all('div', CSS_DESCRIPTION)
    vendor_list = []
    for vendors_div in soup.find_all(id=CSS_VENDOR_LIST):
        vendors = vendors_div.descendants
        for vendor in vendors:
            if vendor.name == 'div' and vendor.get('class', '') == ['editableListItem']:
                vendor_list.append(vendor.text.strip())
    vendor_list = ', '.join(vendor_list)
    title = find_by_label(soup, CSS_TITLE)
    organization = find_by_label(soup, CSS_ORGANIZATION)
    reference = find_by_label(soup, CSS_REFERENCE)
    tender_fields = {
        'source': 'UNGM',
        'title': to_unicode(title.string),
        'organization': to_unicode(organization.string),
        'reference': to_unicode(reference.string.strip()),
        'description': to_unicode(str(description[0])),
    }
    award_date = find_by_label(soup, CSS_AWARD_DATE)
    value = find_by_label(soup, CSS_VALUE)
    winner_fields = {
        'award_date': string_to_date(award_date.string) or date.today(),
        'vendor': vendor_list,
        'value': float(value.string or 0) if value.string
        else None
    }
    if winner_fields['value']:
        winner_fields['currency'] = 'USD'

    return tender_fields, winner_fields


def parse_winners_list(html):
    """Parse a list of contract awards and return a list winners
    Example: [{reference: ... , url: ...}, ...]
    """

    soup = BeautifulSoup(html, 'html.parser')
    references = soup.find_all('div', attrs={'data-description': CSS_REFERENCE})
    urls = soup.find_all('div', attrs={'class': CSS_LIST_TITLE})
    winners_list = [
        {
            'reference': references[i].span.string.strip(),
            'url': ENDPOINT_URI + urls[i].a['href']
        }
        for i in range(len(references))
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
