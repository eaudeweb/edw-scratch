from flask import Blueprint, render_template

from scratch.models import Tender, Winner

views = Blueprint(__name__, 'views')


@views.route('/')
@views.route('/tenders')
def homepage():
    """ Display a list of tenders from local database.
    """

    tenders = Tender.query.all()

    return render_template('homepage.html', tenders=tenders)

@views.route('/award_winners')
def award_winners():
    """ Display a list of contract awards from local database.
    """

    winners = Winner.query.all()

    return render_template('award_winners.html', winners=winners)
