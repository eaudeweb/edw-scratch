from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy import desc

from scratch.models import Tender, Winner, db
from scratch.forms import TendersFilter, WinnerFilter, MAX, STEP


views = Blueprint(__name__, 'views')


@views.route('/')
@views.route('/tenders')
def tenders():
    if 'reset' in request.args:
        return redirect(url_for('.tenders'))

    organization = request.args.get('organization')
    status = request.args.get('status')
    favourite = request.args.get('favourite')

    tenders_qs = Tender.query.filter_by(hidden=False)
    if organization:
        tenders_qs = tenders_qs.filter_by(organization=organization)
    if status == 'closed':
        tenders_qs = tenders_qs.filter(Tender.winner != None)
    elif status == 'open':
        tenders_qs = tenders_qs.filter(Tender.winner == None)
    if favourite in ('True', 'False'):
        tenders_qs = tenders_qs.filter_by(favourite=eval(favourite))

    return render_template(
        'tenders.html',
        tenders=tenders_qs.order_by(desc(Tender.published)).all(),
        filter_form=TendersFilter(
            organization=organization,
            status=status,
            favourite=favourite,
        ),
        reset=organization or status or favourite
    )


@views.route('/winners')
def winners():

    if 'reset' in request.args:
        return redirect(url_for('.winners'))

    organization = request.args.get('organization')
    vendor = request.args.get('vendor')
    value = request.args.get('value')

    winners_qs = Winner.query.filter(
        Winner.tender.has(hidden=False)
    )
    if organization:
        winners_qs = winners_qs.filter(
            Winner.tender.has(organization=organization)
        )
    if vendor:
        winners_qs = winners_qs.filter_by(vendor=vendor)
    if value:
        if value == 'max':
            winners_qs = winners_qs.filter(Winner.value >= MAX)
        else:
            winners_qs = winners_qs.filter(
                Winner.value >= int(value),
                Winner.value <= int(value) + STEP
            )

    return render_template(
        'winners.html',
        winners=winners_qs.order_by(desc(Winner.award_date)).all(),
        filter_form=WinnerFilter(
            organization=organization,
            vendor=vendor,
            value=value,
        ),
        reset=organization or vendor or value
    )


@views.route('/tender/<tender_id>')
def tender(tender_id):
    tender_object = Tender.query.get(tender_id)

    return render_template('tender.html', tender=tender_object)


@views.route('/search')
def search():
    query = request.args.get('query')

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


@views.route('/toggle/<attribute>/<tender_id>')
def toggle(tender_id, attribute):
    if not attribute in ('favourite', 'hidden'):
        return ''
    tender_object = Tender.query.get_or_404(tender_id)
    setattr(tender_object, attribute, not getattr(tender_object, attribute))
    db.session.commit()
    return '{0}'.format(getattr(tender_object, attribute))
