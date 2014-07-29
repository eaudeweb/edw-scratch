from flask import Blueprint, render_template, request, redirect, url_for

from scratch.models import Tender, Winner
from scratch.forms import TendersFilter, WinnerFilter, MAX, STEP


views = Blueprint(__name__, 'views')


@views.route('/', methods=['GET', 'POST'])
@views.route('/tenders', methods=['GET', 'POST'])
def tenders():
    """ Display a list of tenders from local database.
    """
    if request.method == 'GET':
        filter_form = TendersFilter()
        tenders = Tender.query.all()

    if request.method == 'POST':
        if 'reset' in request.form:
            return redirect(url_for('.tenders'))
        organization = request.form['organization']
        title = request.form['title']
        status = request.form['status']
        filter_form = TendersFilter(
            organization=organization,
            title=title,
            status=status,
        )
        if filter_form.validate():
            tenders = Tender.query
            if organization:
                tenders = tenders.filter_by(organization=organization)
            if title:
                tenders = tenders.filter_by(title=title)
            if status == 'closed':
                tenders = tenders.filter(Tender.winner != None)
            elif status == 'open':
                tenders = tenders.filter(Tender.winner == None)

    return render_template(
        'tenders.html',
        tenders=tenders,
        filter_form=filter_form,
    )


@views.route('/winners', methods=['GET', 'POST'])
def winners():
    """ Display a list of contract awards from local database.
    """

    if request.method == 'GET':
        filter_form = WinnerFilter()
        winners = Winner.query.all()

    if request.method == 'POST':
        if 'reset' in request.form:
            return redirect(url_for('.winners'))
        organization = request.form['organization']
        vendor = request.form['vendor']
        value = request.form['value']

        filter_form = WinnerFilter(
            organization=organization,
            vendor=vendor,
            value=value,
        )
        if filter_form.validate():
            winners = Winner.query
            if organization:
                winners = winners.filter(
                    Winner.tender.has(organization=organization)
                )
            if vendor:
                winners = winners.filter_by(vendor=vendor)
            if value:
                if value == 'max':
                    winners = winners.filter(Winner.value >= MAX)
                else:
                    winners = winners.filter(
                        Winner.value >= int(value),
                        Winner.value <= int(value) + STEP
                    )
            winners = winners.all()

    return render_template(
        'winners.html',
        winners=winners,
        filter_form=filter_form,
    )


@views.route('/tender/<tender_id>', methods=['GET'])
def tender(tender_id):
    tender = Tender.query.get(tender_id)

    return render_template('tender.html', tender=tender)


@views.route('/search', methods=['GET'])
def search():
    query = request.args['query']
    if query:
        results = Tender.query.whoosh_search(query, 20).all()
    else:
        results = {}
        query = ''

    return render_template(
        'search.html',
        query=query,
        results=results,
    )
