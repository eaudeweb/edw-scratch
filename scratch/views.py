from flask import Blueprint, render_template

from scratch.models import Tender

views = Blueprint(__name__, 'views')


@views.route('/')
def homepage():
    """ Display a list of tenders from local database.
    """

    tenders = Tender.query.all()

    return render_template('homepage.html', tenders=tenders)
