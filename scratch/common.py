LIVE_ENDPOINT_URI = 'https://www.ungm.org'
TENDERS_ENDPOINT_URI = 'https://www.ungm.org/Public/Notice'
WINNERS_ENDPOINT_URI = 'https://www.ungm.org/Public/ContractAward'
SEARCH_UNSPSCS_URI = 'https://www.ungm.org/UNSPSC/Search'

HEADERS = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.5',
    'Content-Type': 'application/json; charset=UTF-8',
    'Host': 'www.ungm.org',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:31.0)'
    ' Gecko/20100101 Firefox/31.0',
    'X-Requested-With': 'XMLHttpRequest',
}
PAYLOAD = {
    'tenders': {
        'PageIndex': 0,
        'PageSize': 15,
        'NoticeTASStatus': [],
        'Description': '',
        'Title': '',
        'DeadlineFrom': '',
        'SortField': 'DatePublished',
        'UNSPSCs': [],
        'Countries': [],
        'Agencies': [],
        'PublishedTo': '',
        'SortAscending': False,
        'isPicker': False,
        'PublishedFrom': '',
        'NoticeTypes': [],
        'Reference': '',
        'DeadlineTo': '',
    },
    'winners': {
        'PageIndex': 0,
        'PageSize': 15,
        'Title': '',
        'Description': '',
        'Reference': '',
        'Supplier': '',
        'AwardFrom': '',
        'AwardTo': '',
        'Countries': [],
        'Agencies': [],
        'UNSPSCs': [],
        'SortField': 'AwardDate',
        'SortAscending': False,
    },
    'unspsc': {
        'filter': '',
        'isreadOnly': False,
        'showSelectAsParent': False,
    }
}
