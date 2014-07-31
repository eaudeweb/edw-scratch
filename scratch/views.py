from flask import Blueprint, render_template, request, redirect, url_for

from scratch.models import Tender, Winner, TenderDocument
from scratch.forms import TendersFilter, WinnerFilter, MAX, STEP


views = Blueprint(__name__, 'views')


@views.route('/', methods=['GET'])
@views.route('/tenders', methods=['GET'])
def tenders():

    if 'reset' in request.args:
        return redirect(url_for('.tenders'))

    organization = request.args.get('organization')
    title = request.args.get('title')
    status = request.args.get('status')

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
        tenders=tenders.all(),
        filter_form=TendersFilter(
            organization=organization,
            title=title,
            status=status,
        ),
    )


@views.route('/winners', methods=['GET'])
def winners():

    if 'reset' in request.args:
        return redirect(url_for('.winners'))

    organization = request.args.get('organization')
    vendor = request.args.get('vendor')
    value = request.args.get('value')

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

    return render_template(
        'winners.html',
        winners=winners.all(),
        filter_form=WinnerFilter(
            organization=organization,
            vendor=vendor,
            value=value,
        ),
    )


@views.route('/tender/<tender_id>', methods=['GET'])
def tender(tender_id):
    tender = Tender.query.get(tender_id)

    return render_template('tender.html', tender=tender)


@views.route('/search', methods=['GET'])
def search():
    query = request.args['query']
    results = []

    def _model_search(m):
        return m.query.whoosh_search(query).all()

    if query:
        for model in [Tender, TenderDocument, Winner]:
            results += _model_search(model)

    return render_template(
        'search.html',
        query=query,
        results=results,
    )
