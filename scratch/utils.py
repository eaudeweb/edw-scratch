import os
import tarfile
from datetime import datetime, date, timedelta
from random import randint
from time import sleep


def string_to_date(string_date):
    if string_date:
        return datetime.strptime(string_date, '%d-%b-%Y').date()
    return None


def string_to_datetime(string_date):
    if string_date:
        return datetime.strptime(string_date, '%d-%b-%Y %H:%M')
    return None


def to_unicode(string):
    if not string or isinstance(string, unicode):
        return string
    else:
        return unicode(string, 'utf8')


def days_ago(days):
    return date.today() - timedelta(days=days)


def save_file(path, filename, content):
    if not os.path.exists(path):
        os.makedirs(path)
    file_path = os.path.join(path, filename)
    with open(file_path, "wb") as f:
        f.write(content)
    return file_path


def extract_data(archive_path, extract_path):
    tf = tarfile.open(archive_path, 'r:gz')
    tf.extractall(extract_path)
    return tf.getnames()[0]


def random_sleeper(func):
    def inner(self, *args, **kwargs):
        sleep(randint(2, 5))
        return func(self, *args, **kwargs)
    return inner


def get_local_gmt():
    d = datetime.now() - datetime.utcnow()
    return round(float(d.total_seconds()) / 3600)
