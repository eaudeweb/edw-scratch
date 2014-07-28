import requests
import urllib2


LIVE_ENDPOINT_URI = 'https://www.ungm.org'
ENDPOINT_URI = 'http://localhost:8080'
TENDERS_RELATIVE_PATH = '/Public/Notice'
WINNERS_RELATIVE_PATH = '/Public/ContractAward'


def open_file_and_read(filename):
    with open(filename, 'r') as fin:
        data = fin.read()

    return data


def request_tenders_list():
    response = requests.get(
        ENDPOINT_URI + TENDERS_RELATIVE_PATH + '/tender_notices.html'
    )
    if response.status_code == 200:
        return response.content


def request_winners_list():
    response = requests.get(
        ENDPOINT_URI + WINNERS_RELATIVE_PATH + '/contract_winners.html'
    )
    if response.status_code == 200:
        return response.content


def replace_get_param(func):
    def replacer(url):
        splitted_url = url.split('?docId=')
        url = splitted_url[0] + '/' + splitted_url[1]
        return func(url)
    return replacer


def replace_endpoint(func):
    def replacer(url):
        url = url.replace(LIVE_ENDPOINT_URI, ENDPOINT_URI)
        return func(url)
    return replacer


@replace_endpoint
def request(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content


@replace_get_param
@replace_endpoint
def request_document(url):
    try:
        response = urllib2.urlopen(url)
        return response.read()
    except urllib2.HTTPError:
        return None
