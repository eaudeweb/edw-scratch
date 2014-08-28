import os
from urllib import urlencode
from datetime import datetime, date

import requests
from bs4 import BeautifulSoup
from flask import current_app as app

from scratch.models import (
    last_update, add_worker_log, save_tender, save_winner,
)
from scratch.utils import days_ago, save_file, extract_data, random_sleeper


def get_publication_date(row):
    cells = row.find_all('td')
    publication_date = datetime.strptime(cells[1].text.strip(), '%d-%m-%Y')
    return publication_date.date()


def get_archives_path():
    return os.path.join(app.config.get('FILES_DIR'), 'TED_archives')


def update_winner(winner, soup):
    award_date = soup.find('contract_award_date')
    if award_date:
        fields = {c.name: int(c.text) for c in award_date.contents}
        winner['award_date'] = date(**fields)
    vendor = soup.find('economic_operator_name_address') or \
        soup.find('contact_data_without_responsible_name_chp')
    if vendor:
        winner['vendor'] = vendor.officialname.text \
            if vendor.officialname else None
    value = soup.find('value_cost')
    if value:
        winner['value'] = value.get('fmtval')
        winner['currency'] = value.parent.get('currency')


@random_sleeper
def request(session, request_type, *args, **kwargs):
    return getattr(session, request_type)(*args, **kwargs)


class TEDWorker(object):
    HOMEPAGE_URL = 'http://ted.europa.eu/TED/main/HomePage.do'
    DOWNLOAD_URL = 'http://ted.europa.eu/TED/misc/bulkDownloadExport.do'

    def __init__(self, archives=[]):
        self.path = get_archives_path()
        self.archives = archives

    def _initialize_session(self):
        session = requests.Session()
        request(session, 'get', self.HOMEPAGE_URL)

        data = {'action': 'gp'}
        additional_params = {'pid': 'secured'}
        url = '?'.join((self.HOMEPAGE_URL, urlencode(additional_params)))
        resp = request(session, 'post', url, data=data, allow_redirects=True)

        a = BeautifulSoup(resp.content).find('a', {'title': 'External'})
        resp = request(session, 'get', a.get('href'))

        form = BeautifulSoup(resp.content).find('form', {'id': 'loginForm'})
        data = {i.get('name'): i.get('value') for i in form.find_all('input')}
        data['username'] = app.config.get('TED_USERNAME')
        data['password'] = app.config.get('TED_PASSWORD')
        data['selfHost'] = 'webgate.ec.europa.eu'
        data['timeZone'] = 'GMT+03:00'
        url = form.get('action')
        resp = request(session, 'post', url, data=data, allow_redirects=True)

        form = BeautifulSoup(resp.content).find(
            'form', {'id': 'showAccountDetailsForm'})
        data = {i.get('name'): i.get('value') for i in form.find_all('input')}
        url = form.get('action')
        resp = request(session, 'post', url, data=data, allow_redirects=True)

        a = BeautifulSoup(resp.content).select('p.note > a')[0]
        request(session, 'get', a.get('href'))
        return session

    def _download_by_id(self, archive_id):
        data = {'action': 'dlTedExport'}
        additional_params = {'dlTedExportojsId': archive_id}
        url = '?'.join((self.DOWNLOAD_URL, urlencode(additional_params)))
        resp = request(self.session, 'post', url, data=data,
                       allow_redirects=True)

        if resp.status_code == 200:
            archive_name = archive_id + '.tgz'
            archive_path = save_file(self.path, archive_name, resp.content)
            self.archives.append(archive_path)

    def download_latest(self):
        self.session = self._initialize_session()
        resp = request(self.session, 'get', self.DOWNLOAD_URL)
        soup = BeautifulSoup(resp.content)
        rows = soup.select('table#availableBulkDownloadRelease tr')[1:]
        last_date = last_update('TED') or days_ago(30)
        for row in rows:
            publication_date = get_publication_date(row)
            if publication_date <= last_date:
                break
            archive_id = row.find('input', {'type': 'hidden'}).get('value')
            self._download_by_id(archive_id)
        add_worker_log('TED', get_publication_date(rows[0]))

    def extract_archives(self):
        self.folder_names = []
        for archive_path in self.archives:
            folder_name = extract_data(archive_path, self.path)
            self.folder_names.append(folder_name)


class TEDParser(object):

    def __init__(self, path='', folder_names=[]):
        path = path or get_archives_path()
        self.xml_files = [
            os.path.join(path, folder, xml_file)
            for folder in folder_names
            for xml_file in os.listdir(os.path.join(path, folder))
        ]
        self.folders = [os.path.join(path, folder) for folder in folder_names]

    def _parse_notice(self, content):
        soup = BeautifulSoup(content)

        tender = {}
        tender['reference'] = soup.find('ted_export').get('doc_id')
        tender['notice_type'] = soup.find('td_document_type').text
        parts = [e.text for e in soup.find('ml_ti_doc', {'lg': 'EN'}).children]
        tender['title'] = u'{0}-{1}: {2}'.format(*parts)
        tender['organization'] = (soup.find('aa_name', {'lg': 'EN'}) or
                                  soup.find('aa_name')).text
        published_str = soup.find('date_pub').text
        tender['published'] = datetime.strptime(published_str, '%Y%m%d').date()

        deadline = soup.find('dt_date_for_submission')
        if deadline:
            try:
                deadline = datetime.strptime(deadline.text, '%Y%m%d %H:%M')
            except ValueError:
                deadline = datetime.strptime(deadline.text, '%Y%m%d')
        tender['deadline'] = deadline

        description = soup.find('SHORT_CONTRACT_DESCRIPTION')
        tender['description'] = description.text if description else ''
        url = soup.find('uri_doc')
        tender['url'] = url.text.replace(url.get('lg'), 'EN')
        tender['source'] = 'TED'

        winner = {}
        if tender['notice_type'] == 'Contract award':
            update_winner(winner, soup)

        return tender, winner

    def _filter_notices(self):
        for xml_file in self.xml_files[:]:
            with open(xml_file, 'r') as f:
                soup = BeautifulSoup(f.read())
                cpv_codes = set([c.get('code') for c in soup.find('cpv_code')])
                if not cpv_codes & set(app.config.get('CPV_CODES', [])):
                    self.xml_files.remove(xml_file)
                    os.remove(xml_file)

    def parse_notices(self):
        self._filter_notices()
        for xml_file in self.xml_files:
            with open(xml_file, 'r') as f:
                tender, winner = self._parse_notice(f.read())
                if winner:
                    save_winner(tender, winner)
                else:
                    save_tender(tender)
            os.remove(xml_file)

    def __del__(self):
        for folder in self.folders:
            os.rmdir(folder)
