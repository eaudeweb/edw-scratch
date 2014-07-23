from datetime import datetime, date


def string_to_date(string_date):
    if string_date:
        return datetime.strptime(string_date, '%d-%b-%Y').date()
    return None


def string_to_datetime(string_date):
    if string_date:
        return datetime.strptime(string_date, '%d-%b-%Y %H:%M')
    return None
