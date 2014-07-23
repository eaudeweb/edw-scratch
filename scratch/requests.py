def request_tenders():
    filename = 'testing/example_html/filtered_tender_notices.html'
    with open(filename, 'r') as fin:
        data = fin.read()

    return data
