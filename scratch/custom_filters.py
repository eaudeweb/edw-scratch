from datetime import datetime, date

from utils import days_ago

from flask import url_for


def time_to_deadline(d, breakline=False):
    if d is None:
        return 'Unknown'
    now = datetime.now()
    if now > d:
        return 'EXPIRED'
    td = d - now
    hours = td.seconds/3600
    minutes = (td.seconds/60) % 60
    deadline = '{days} days, {h} hours </br>{m} minutes'.format(
        days=td.days, h=hours, m=minutes
    )
    return deadline.replace(' </br>', ', ') if not breakline else deadline


def datetime_filter(d):
    if d is None:
        return 'Unknown'
    if type(d) is date:
        return d.strftime('%d %B %Y')
    elif type(d) is datetime:
        return d.strftime('%d %B %Y - %H:%M:%S')
    return d


def get_color_class(tender, class_value=''):
    if tender.winner:
        return class_value + 'bg-danger'
    if tender.favourite:
        return class_value + 'bg-warning'
    if tender.published > days_ago(7):
        return class_value + 'bg-info'
    return class_value


def get_favorite_class(tender):
    return "fa fa-lg fa-star" if tender.favourite else "fa fa-lg fa-star-o"


def get_filename(tender_id, name):
    return url_for(
        'files',
        filename='{folder}/{doc_name}'.format(
            folder=tender_id,
            doc_name=name
        )
    )
