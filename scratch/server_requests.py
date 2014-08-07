import requests
import urllib2
from datetime import datetime
import json
from flask import current_app as app

LOCAL_ENDPOINT_URI = 'http://localhost:8080'
LIVE_ENDPOINT_URI = 'https://www.ungm.org'
TENDERS_ENDPOINT_URI = 'https://www.ungm.org/Public/Notice'
WINNERS_ENDPOINT_URI = 'https://www.ungm.org/Public/ContractAward'
SEARCH_UNSPSCS_URI = 'https://www.ungm.org/UNSPSC/Search'

HEADERS = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.5',
    'Content-Type': 'application/json; charset=UTF-8',
    'Host': 'www.ungm.org',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:31.0)'
    ' Gecko/20100101 Firefox/31.0',
    'X-Requested-With': 'XMLHttpRequest',
}
PAYLOAD = {
    'tenders': {
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
    },
    'winners': {
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
    },
    'unspsc': {
        'filter': '',
        'isreadOnly': False,
        'showSelectAsParent': False,
    }
}


def get_request_class(public=True):
    return UNGMrequester() if public else LOCALrequester()


class Requester(object):

    def get_request(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.content

        return None

    def request_document(self, url):
        try:
            response = urllib2.urlopen(url)
            return response.read()
        except urllib2.HTTPError:
            return None


class UNGMrequester(Requester):
    def get_data(self, category):
        payload = PAYLOAD[category]
        if category == 'tenders':
            today = datetime.now().strftime('%d-%b-%Y')
            payload['DeadlineFrom'] = payload['PublishedTo'] = today
        payload['UNSPSCs'] = app.config.get('UNSPSCs', {}).get(category, [])
        return json.dumps(payload)

    def request_tenders_list(self):
        get_url = TENDERS_ENDPOINT_URI
        post_url = get_url + '/Search'
        data = self.get_data('tenders')
        return self.post_request(get_url, post_url, data)

    def request_winners_list(self):
        get_url = WINNERS_ENDPOINT_URI
        post_url = get_url + '/Search'
        data = self.get_data('winners')
        return self.post_request(get_url, post_url, data)

    def post_request(self, get_url, post_url, data, headers=HEADERS,
                     content_type=None):
        """
        AJAX-like POST request. Does a GET initially to receive cookies that
        are used to the subsequent POST request.
        """
        resp = requests.get(get_url)
        cookies = dict(resp.cookies)
        cookies.update({'UNGM.UserPreferredLanguage': 'en'})

        headers.update({
            'Cookie': '; '.join(
                ['{0}={1}'.format(k, v) for k, v in cookies.iteritems()]),
            'Referer': get_url,
            'Content-Length': len(data),
        })
        if content_type:
            headers.update({'Content-Type': content_type})

        resp = requests.post(post_url, data=data, cookies=cookies,
                             headers=headers)
        if resp.status_code == 200:
            return resp.content
        return None


class LOCALrequester(Requester):

    def replace_endpoint(self, url):
        return url.replace(LIVE_ENDPOINT_URI, LOCAL_ENDPOINT_URI)

    def get_request(self, url):
        url = self.replace_endpoint(url) + '.html'
        return super(LOCALrequester, self).get_request(url)

    def request_tenders_list(self):
        url = TENDERS_ENDPOINT_URI + '/tender_notices'
        return self.get_request(url)

    def request_winners_list(self):
        url = WINNERS_ENDPOINT_URI
        url += '/contract_winners'
        return self.get_request(url)

    def request_document(self, url):
        url = self.replace_endpoint(url)
        splitted_url = url.split('?docId=')
        url = splitted_url[0] + '/' + splitted_url[1]
        return super(LOCALrequester, self).request_document(url)
