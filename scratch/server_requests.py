import requests
import urllib2
from datetime import datetime
import json
from flask import current_app


LIVE_ENDPOINT_URI = 'https://www.ungm.org'
LOCAL_ENDPOINT_URI = 'http://localhost:8080'
TENDERS_ENDPOINT_URI = 'https://www.ungm.org/Public/Notice'
WINNERS_ENDPOINT_URI = 'https://www.ungm.org/Public/ContractAward'

HEADERS = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.5',
    'Content-Length': '320',
    'Content-Type': 'application/json; charset=UTF-8',
    'Host': 'www.ungm.org',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:31.0)'
    ' Gecko/20100101 Firefox/31.0',
    'X-Requested-With': 'XMLHttpRequest',
}
PAYLOAD_TENDERS = {
    'PageIndex': 0,
    'PageSize': 15,
    'NoticeTASStatus': [],
    'Description': '',
    'Title': '',
    'DeadlineFrom': '',
    'SortField': 'DatePublished',
    'UNSPSCs': [],
    'Countries': [],
    'Agencies': [],
    'PublishedTo': '',
    'SortAscending': False,
    'isPicker': False,
    'PublishedFrom': '',
    'NoticeTypes': [],
    'Reference': '',
    'DeadlineTo': '',
}
PAYLOAD_WINNERS = {
    'PageIndex': 0,
    'PageSize': 15,
    'Title': '',
    'Description': '',
    'Reference': '',
    'Supplier': '',
    'AwardFrom': '',
    'AwardTo': '',
    'Countries': [],
    'Agencies': [],
    'UNSPSCs': [],
    'SortField': 'AwardDate',
    'SortAscending': False,
}


def replace_endpoint(url):
    return url.replace(LIVE_ENDPOINT_URI, LOCAL_ENDPOINT_URI)


def get_request(url, public):
    if not public:
        url = replace_endpoint(url)

    response = requests.get(url)
    if response.status_code == 200:
        return response.content

    return None


def post_request(get_url, payload, UNSPSC_category, headers=HEADERS):
    """
    AJAX-like POST request. Does a GET initially to receive cookies that
    are used to the subsequent POST request.
    """
    resp = requests.get(get_url)
    cookies = dict(resp.cookies)
    cookies.update({'UNGM.UserPreferredLanguage': 'en'})

    headers.update({
        'Cookie': ';'.join(
            ['{0}={1}'.format(k, v) for k, v in cookies.iteritems()]),
        'Referer': get_url,
    })

    UNSPSCs = current_app.config.get('UNSPSCs', {})
    payload['UNSPSCs'] = UNSPSCs.get(UNSPSC_category, [])

    post_url = get_url + '/Search'
    resp = requests.post(post_url, data=json.dumps(payload), cookies=cookies,
                         headers=headers)
    if resp.status_code == 200:
        return resp.content

    return None


def request_tenders_list(public):
    url = TENDERS_ENDPOINT_URI
    if not public:
        url += '/tender_notices.html'
        return get_request(url, public)

    payload = PAYLOAD_TENDERS
    today = datetime.now().strftime('%d-%b-%Y')
    payload['DeadlineFrom'] = payload['PublishedTo'] = today
    return post_request(url, payload, 'tenders')


def request_winners_list(public):
    url = WINNERS_ENDPOINT_URI
    if not public:
        url += '/contract_winners.html'
        return get_request(url, public)

    return post_request(url, PAYLOAD_WINNERS, 'winners')


def request_document(url, public):
    if not public:
        url = replace_endpoint(url)
        splitted_url = url.split('?docId=')
        url = splitted_url[0] + '/' + splitted_url[1]

    try:
        response = urllib2.urlopen(url)
        return response.read()
    except urllib2.HTTPError:
        return None
