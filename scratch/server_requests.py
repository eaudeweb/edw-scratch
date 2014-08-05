import requests
import urllib2


LIVE_ENDPOINT_URI = 'https://www.ungm.org'
LOCAL_ENDPOINT_URI = 'http://localhost:8080'
TENDERS_ENDPOINT_URI = 'https://www.ungm.org/Public/Notice'
WINNERS_ENDPOINT_URI = 'https://www.ungm.org/Public/ContractAward'


def replace_endpoint(url):
    return url.replace(LIVE_ENDPOINT_URI, LOCAL_ENDPOINT_URI)


def request_tenders_list(public):
    url = TENDERS_ENDPOINT_URI
    if not public:
        url += '/tender_notices.html'

    return request(url, public)


def request_winners_list(public):
    url = WINNERS_ENDPOINT_URI
    if not public:
        url += '/contract_winners.html'

    return request(url, public)


def request(url, public):
    if not public:
        url = replace_endpoint(url)

    response = requests.get(url)
    if response.status_code == 200:
        return response.content

    return None


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
