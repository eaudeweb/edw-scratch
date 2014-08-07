import requests
import urllib2
from datetime import datetime
import json
from flask import current_app as app

from scratch.common import (
    LOCAL_ENDPOINT_URI, LIVE_ENDPOINT_URI, TENDERS_ENDPOINT_URI,
    WINNERS_ENDPOINT_URI, HEADERS, PAYLOAD,
)


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
