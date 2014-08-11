from flask import Flask
import flask.ext.whooshalchemy as whooshalchemy
from flask.ext.assets import Environment, Bundle

from scratch.custom_filters import (
    datetime_filter, get_color_class, get_favorite_class, time_to_deadline
)
from scratch.models import Tender, Winner, db
from scratch.views import (TenderView, TendersView, WinnersView, SearchView,
                           ArchiveView, OverviewView, toggle)


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    assets = Environment(app)
    js = Bundle('js/main.js')
    assets.register('main_js', js)
    whooshalchemy.whoosh_index(app, Tender)
    whooshalchemy.whoosh_index(app, Winner)
    app.config.from_pyfile('settings.py')
    app.jinja_env.filters['datetime'] = datetime_filter
    app.jinja_env.filters['color'] = get_color_class
    app.jinja_env.filters['favourite'] = get_favorite_class
    app.jinja_env.filters['deadline'] = time_to_deadline
    db.init_app(app)
    app.add_url_rule('/tenders/', view_func=TendersView.as_view('tenders'))
    app.add_url_rule('/archive/', view_func=ArchiveView.as_view('archive'))
    app.add_url_rule('/winners/', view_func=WinnersView.as_view('winners'))
    app.add_url_rule('/search/', view_func=SearchView.as_view('search'))
    app.add_url_rule('/tender/<tender_id>',
                     view_func=TenderView.as_view('tender'))
    app.add_url_rule('/overview/', view_func=OverviewView.as_view('overview'))
    app.add_url_rule('/toggle/<attribute>/<tender_id>', view_func=toggle)
    return app
