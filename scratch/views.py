from flask import Blueprint, render_template, request

from scratch.models import Tender, Winner
from scratch.forms import OrganizationFilter


views = Blueprint(__name__, 'views')


@views.route('/', methods=['GET', 'POST'])
@views.route('/tenders', methods=['GET', 'POST'])
def homepage():
    """ Display a list of tenders from local database.
    """

    if request.method == 'GET':
        filter_form = OrganizationFilter()
        tenders = Tender.query.all()

    if request.method == 'POST':
        if request.form['type'] == 'Reset filters':
            filter_form = OrganizationFilter()
            tenders = Tender.query.all()
            pass
        else:
            organization = request.form['organization']
            title = request.form['title']
            filter_form = OrganizationFilter(
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


@views.route('/award_winners')
def award_winners():
    """ Display a list of contract awards from local database.
    """

    winners = Winner.query.all()

    return render_template('award_winners.html', winners=winners)
