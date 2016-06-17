import os
from datetime import datetime, date, timedelta
from ftplib import FTP

from bs4 import BeautifulSoup, element
from flask import current_app as app

from scratch.models import last_update, add_worker_log, save_tender, save_winner
from scratch.utils import days_ago, extract_data, random_sleeper


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
    FTP_URL = 'ted.europa.eu'

    def __init__(self, archives=[]):
        self.path = get_archives_path()
        self.archives = archives

    def get_archive_name(self, last_date, archives):
        starting_name = last_date.strftime('%Y%m%d')
        for archive_name in archives:
            if archive_name.startswith(starting_name):
                return archive_name
        return None

    def ftp_download(self):
        ftp = FTP(self.FTP_URL)
        ftp.login(user='guest', passwd='guest')

        last_date = last_update('TED') or \
            days_ago(app.config.get('TED_DAYS_AGO', 30))
        last_month = last_date.strftime('%m')
        last_year = last_date.strftime('%Y')

        ftp.cwd('daily-packages/{year}/{month}'.format(
            year=last_year, month=last_month))
        archives = ftp.nlst()
        today = date.today()

        while last_date < today:
            archive_name = self.get_archive_name(last_date, archives)
            if archive_name:
                if not os.path.exists(self.path):
                    os.makedirs(self.path)
                file_path = os.path.join(self.path, archive_name)
                with open(file_path, 'wb') as f:
                    ftp.retrbinary('RETR %s' % archive_name,
                                   lambda data: f.write(data))
                self.archives.append(file_path)
            add_worker_log('TED', last_date)

            last_date += timedelta(1)

            if last_year != last_date.strftime('%Y'):
                last_year = last_date.strftime('%Y')
                last_month = last_date.strftime('%m')
                ftp.cwd('../../{}/{}'.format(last_year, last_month))
                archives = ftp.nlst()
            elif last_month != last_date.strftime('%m'):
                last_month = last_date.strftime('%m')
                ftp.cwd('../{}'.format(last_month))
                archives = ftp.nlst()

        ftp.quit()

    def extract_archives(self):
        self.folder_names = []
        for archive_path in self.archives:
            folder_name = extract_data(archive_path, self.path)
            self.folder_names.append(folder_name)

    def parse_notices(self):
        for archive_path in self.archives:
            folder_name = extract_data(archive_path, self.path)
            p = TEDParser(self.path, [folder_name])
            p.parse_notices()


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
        parts = [e.text for e in soup.find('ml_ti_doc', {'lg': 'EN'}).children
                if isinstance(e, element.Tag)]
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

        section = soup.find('contract', {'lg': 'EN'})
        desc = section.find('short_contract_description') if section else None
        tender['description'] = ''.join([str(e) for e in desc.contents]) \
            if desc else ''
        tender['description'] = tender['description'].decode('utf-8')
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

                cpv_elements = soup.find_all('cpv_code') \
                    or soup.find_all('original_cpv')
                cpv_codes = set([c.get('code') for c in cpv_elements])

                doc_type = soup.find('td_document_type').text
                country = soup.find('iso_country').get('value')
                auth_type = soup.find('aa_authority_type').text

                accept_notice = (
                    cpv_codes & set(app.config.get('CPV_CODES', [])) and
                    doc_type in app.config.get('TED_DOC_TYPES', []) and
                    country in app.config.get('TED_COUNTRIES', []) and
                    auth_type == app.config.get('TED_AUTH_TYPE', ''))

                if not accept_notice:
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
