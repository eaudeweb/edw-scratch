import requests


LIVE_ENDPOINT_URI = 'https://www.ungm.org'
TEST_ENDPOINT_URI = 'http://localhost:8080'


def open_file_and_read(filename):
    with open(filename, 'r') as fin:
        data = fin.read()

    return data


def request_tenders_list():
    response = requests.get(
        TEST_ENDPOINT_URI+'/Public/Notice/tender_notices.html'
    )
    if response.status_code == 200:
        return response.content


def request_winners_list():
    filename = 'testing/example_html/filtered_contract_winners.html'
    return open_file_and_read(filename)


def replace_endpoint(func):
    def replacer(url):
        url = url.replace(LIVE_ENDPOINT_URI, TEST_ENDPOINT_URI)
        return func(url)
    return replacer


@replace_endpoint
def request(url=None):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
