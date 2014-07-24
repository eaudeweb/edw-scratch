import requests


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


def replace_endpoint(func):
    def replacer(url):
        url = url.replace(LIVE_ENDPOINT_URI, ENDPOINT_URI)
        return func(url)
    return replacer


@replace_endpoint
def request(url=None):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
