from datetime import datetime, date, timedelta


def string_to_date(string_date):
    if string_date:
        return datetime.strptime(string_date, '%d-%b-%Y').date()
    return None


def string_to_datetime(string_date):
    if string_date:
        return datetime.strptime(string_date, '%d-%b-%Y %H:%M')
    return None


def to_unicode(string):
    if isinstance(string, unicode):
        return string
    else:
        return unicode(string, 'utf8')


def days_ago(days):
    return date.today()-timedelta(days=days)
