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
    if tender.favourite:
        return class_value + 'bg-warning'
    if tender.published > days_ago(21):
        return class_value + 'bg-info'
    return class_value


def get_favorite_class(tender):
    return "fa fa-lg fa-star" if tender.favourite else "fa fa-lg fa-star-o"
