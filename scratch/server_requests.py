import requests
import urllib2
import json
from datetime import datetime
from random import randint
from time import sleep
from flask import current_app as app

from scratch.common import (
    LOCAL_ENDPOINT_URI, LIVE_ENDPOINT_URI, TENDERS_ENDPOINT_URI,
    WINNERS_ENDPOINT_URI, HEADERS, PAYLOAD,
)
from scratch.utils import random_sleeper


def get_request_class(public=True):
    return UNGMrequester() if public else LOCALrequester()


class Requester(object):

    @random_sleeper
    def get_request(self, url):
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            return None

        if response.status_code == 200:
            return response.content
        return None

    @random_sleeper
    def request_document(self, url):
        try:
            response = urllib2.urlopen(url)
            return response.read()
        except urllib2.HTTPError:
            return None

    def request_tenders_list(self):
        return self.request(self.TENDERS_ENDPOINT_URI)

    def request_winners_list(self):
        return self.request(self.WINNERS_ENDPOINT_URI)


class UNGMrequester(Requester):
    TENDERS_ENDPOINT_URI = TENDERS_ENDPOINT_URI
    WINNERS_ENDPOINT_URI = WINNERS_ENDPOINT_URI

    def get_data(self, url):
        category = 'tenders' if 'Notice' in url else 'winners'
        payload = PAYLOAD[category]
        if category == 'tenders':
            today = datetime.now().strftime('%d-%b-%Y')
            payload['DeadlineFrom'] = payload['PublishedTo'] = today
        payload['UNSPSCs'] = app.config.get('UNSPSC_CODES', [])
        return json.dumps(payload)

    def request(self, url):
        for i in range(0, app.config.get('MAX_UNGM_REQUESTS', 1)):
            resp = self.post_request(url, url + '/Search', self.get_data(url))
            if resp:
                return resp
            sleep(randint(10, 15))

    @random_sleeper
    def post_request(self, get_url, post_url, data, headers=HEADERS,
                     content_type=None):
        """
        AJAX-like POST request. Does a GET initially to receive cookies that
        are used to the subsequent POST request.
        """
        try:
            resp = requests.get(get_url)
        except requests.exceptions.ConnectionError:
            return None

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

        try:
            sleep(randint(2, 5))
            resp = requests.post(post_url, data=data, cookies=cookies,
                                 headers=headers)
        except requests.exceptions.ConnectionError:
            return None

        if resp.status_code == 200:
            return resp.content
        return None


class LOCALrequester(Requester):

    TENDERS_ENDPOINT_URI = TENDERS_ENDPOINT_URI + '/tender_notices'
    WINNERS_ENDPOINT_URI = WINNERS_ENDPOINT_URI + '/contract_winners'

    def get_request(self, url):
        url = url.replace(LIVE_ENDPOINT_URI, LOCAL_ENDPOINT_URI)
        url += '.html'
        return super(LOCALrequester, self).get_request(url)

    def request(self, url):
        return self.get_request(url)

    def request_document(self, url):
        url = url.replace(LIVE_ENDPOINT_URI, LOCAL_ENDPOINT_URI)
        splitted_url = url.split('?docId=')
        url = splitted_url[0] + '/' + splitted_url[1]
        return super(LOCALrequester, self).request_document(url)
