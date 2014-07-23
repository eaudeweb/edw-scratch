from flask import Blueprint, render_template, request

from scratch.models import Tender, Winner
from scratch.forms import TendersFilter, WinnerFilter, MAX, STEP


views = Blueprint(__name__, 'views')


@views.route('/', methods=['GET', 'POST'])
@views.route('/tenders', methods=['GET', 'POST'])
def homepage():
    """ Display a list of tenders from local database.
    """
    if request.method == 'GET':
        filter_form = TendersFilter()
        tenders = Tender.query.all()

    if request.method == 'POST':
        organization = request.form['organization']
        title = request.form['title']
        filter_form = TendersFilter(
            organization=organization,
            title=title,
        )
        if filter_form.validate():
            tenders = Tender.query
            if organization:
                tenders = tenders.filter_by(organization=organization)
            if title:
                tenders = tenders.filter_by(title=title)
            tenders = tenders.all()

    return render_template(
        'homepage.html',
        tenders=tenders,
        filter_form=filter_form,
    )


@views.route('/award_winners', methods=['GET', 'POST'])
def award_winners():
    """ Display a list of contract awards from local database.
    """

    if request.method == 'GET':
        filter_form = WinnerFilter()
        winners = Winner.query.all()

    if request.method == 'POST':
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
        'award_winners.html',
        winners=winners,
        filter_form=filter_form,
    )


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
