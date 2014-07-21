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
        organization_form = OrganizationFilter()
        tenders = Tender.query.all()

    if request.method == 'POST':
        organization = request.form['organization']
        organization_form = OrganizationFilter(organization=organization)
        if organization_form.validate():
            if organization:
                tenders = Tender.query.filter_by(organization=organization)
            else:
                tenders = Tender.query.all()

    return render_template(
        'homepage.html',
        tenders=tenders,
        organization_form=organization_form,
    )


@views.route('/award_winners')
def award_winners():
    """ Display a list of contract awards from local database.
    """

    winners = Winner.query.all()

    return render_template('award_winners.html', winners=winners)
