def open_file_and_read(filename):
    with open(filename, 'r') as fin:
        data = fin.read()

    return data


def request_tenders_list():
    filename = 'testing/example_html/filtered_tender_notices.html'
    return open_file_and_read(filename)


def request_winners_list():
    filename = 'testing/example_html/filtered_contract_winners.html'
    return open_file_and_read(filename)


def request_tender():
    filename = 'testing/example_html/tender_detail.html'
    return open_file_and_read(filename)


def request_winner():
    filename = 'testing/example_html/winner_detail.html'
    return open_file_and_read(filename)

