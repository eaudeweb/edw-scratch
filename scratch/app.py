import os

from werkzeug import SharedDataMiddleware
from flask import Flask
import flask.ext.whooshalchemy as whooshalchemy
from flask.ext.assets import Environment, Bundle
from scratch.custom_filters import (
    datetime_filter, get_color_class, get_favorite_class, time_to_deadline,
    get_filename, format_digits,
)
from scratch.models import Tender, Winner, db
from scratch.views import (
    TenderView, TendersView, WinnersView, SearchView, ArchiveView, OverviewView,
    toggle, homepage,
)
from scratch.authentication import login_manager, login, logout, auth

_BUNDLE_CSS = (
    'css/main.css',
)

_BUNDLE_JS = (
    'js/main.js',
)

DEFAULT_CONFIG = {
    'USERNAME': 'edw',
    'PASSWORD': 'edw',
}

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = app.config['SECRET_KEY']
    app.config.update(DEFAULT_CONFIG)
    app.config.from_pyfile('settings.py')

    _configure_assets(app)
    _configure_whoosh(app)
    _configure_filters(app)
    _configure_routes(app)
    _configure_uploads(app)

    app.register_blueprint(auth)
    login_manager.init_app(app)
    db.init_app(app)
    
    if app.config.get('SENTRY_DSN'):
        from raven.contrib.flask import Sentry
        Sentry(app)
    return app


def _configure_assets(app):
    assets = Environment(app)
    css = Bundle(*_BUNDLE_CSS, output='gen/static.css')
    js = Bundle(*_BUNDLE_JS, output='gen/static.js')
    assets.register('all_js', js)
    assets.register('all_css', css)


def _configure_whoosh(app):
    whooshalchemy.whoosh_index(app, Tender)
    whooshalchemy.whoosh_index(app, Winner)


def _configure_filters(app):
    app.jinja_env.filters['datetime'] = datetime_filter
    app.jinja_env.filters['color'] = get_color_class
    app.jinja_env.filters['favourite'] = get_favorite_class
    app.jinja_env.filters['deadline'] = time_to_deadline
    app.jinja_env.filters['filename'] = get_filename
    app.jinja_env.filters['format_digits'] = format_digits


def _configure_routes(app):
    app.add_url_rule('/', view_func=homepage)
    app.add_url_rule('/tenders/', view_func=TendersView.as_view('tenders'))
    app.add_url_rule('/archive/', view_func=ArchiveView.as_view('archive'))
    app.add_url_rule('/winners/', view_func=WinnersView.as_view('winners'))
    app.add_url_rule('/search/', view_func=SearchView.as_view('search'))
    app.add_url_rule('/tender/<tender_id>',
                     view_func=TenderView.as_view('tender'))
    app.add_url_rule('/overview/', view_func=OverviewView.as_view('overview'))
    app.add_url_rule('/toggle/<attribute>/<tender_id>', view_func=toggle)
    app.add_url_rule('/login/', methods=["GET", "POST"], view_func=login)
    app.add_url_rule('/logout/', view_func=logout)


def _configure_uploads(app):
    files_path = os.path.join(app.instance_path, 'files')
    app.add_url_rule('/static/files/<filename>', 'files', build_only=True)
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
        '/static/files': files_path
    })
