from datetime import datetime, date

from utils import days_ago


def datetime_filter(d):
    if type(d) is date:
        return d.strftime('%d %B %Y')
    elif type(d) is datetime:
        return d.strftime('%d %B %Y</br>%H:%M:%S')
    return d


def get_color_class(tender, class_value=''):
    if tender.winner:
        return class_value + 'bg-danger'
    if tender.published > days_ago(14):
        return class_value + 'bg-info'
    return class_value
