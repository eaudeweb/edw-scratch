from flask import Blueprint, render_template


views = Blueprint(__name__, 'views')


@views.route('/')
def homepage():
    """ Display a list of tenders from local database.
    """
    return render_template('homepage.html')
