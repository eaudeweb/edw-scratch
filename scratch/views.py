from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy import desc

from scratch.models import Tender, Winner, db
from scratch.forms import TendersFilter, WinnerFilter, MAX, STEP


views = Blueprint(__name__, 'views')


@views.route('/', methods=['GET'])
@views.route('/tenders', methods=['GET'])
def tenders():

    if 'reset' in request.args:
        return redirect(url_for('.tenders'))

    organization = request.args.get('organization')
    status = request.args.get('status')
    favourite = request.args.get('favourite')

    tenders = Tender.query
    if organization:
        tenders = tenders.filter_by(organization=organization)
    if status == 'closed':
        tenders = tenders.filter_by(Tender.winner != None)
    elif status == 'open':
        tenders = tenders.filter(Tender.winner == None)
    if favourite in ('True', 'False'):
        tenders = tenders.filter_by(favourite=eval(favourite))

    return render_template(
        'tenders.html',
        tenders=tenders.order_by(desc(Tender.published)).all(),
        filter_form=TendersFilter(
            organization=organization,
            status=status,
            favourite=favourite,
        ),
        reset=organization or status or favourite
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
        winners=winners.order_by(desc(Winner.award_date)).all(),
        filter_form=WinnerFilter(
            organization=organization,
            vendor=vendor,
            value=value,
        ),
        reset=organization or vendor or value
    )


@views.route('/tender/<tender_id>', methods=['GET'])
def tender(tender_id):
    tender = Tender.query.get(tender_id)

    return render_template('tender.html', tender=tender)


@views.route('/search', methods=['GET'])
def search():
    query = request.args['query']

    def _get_results(m):
        return m.query.whoosh_search(query).all()

    ids = set(
        [x.id for x in _get_results(Tender)] +
        [x.tender_id for x in _get_results(Winner)]
    )

    return render_template(
        'search.html',
        query=query,
        results=Tender.query.filter(Tender.id.in_(ids)).all(),
    )


@views.route('/toggle_favourite/<tender_id>', methods=['GET'])
def toggle_favourite(tender_id):
    tender = Tender.query.get_or_404(tender_id)
    tender.favourite = not tender.favourite
    db.session.commit()
    return ''
