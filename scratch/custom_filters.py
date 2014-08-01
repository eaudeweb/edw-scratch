from datetime import datetime, date


def datetime_filter(d):
    if type(d) is date:
        return d.strftime('%d %B %Y')
    elif type(d) is datetime:
        return d.strftime('%d %B %Y</br>%H:%M:%S')
    return d
