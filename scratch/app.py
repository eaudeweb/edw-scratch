from flask import Flask
from scratch.models import Tender, Winner
import flask.ext.whooshalchemy as whooshalchemy
from flask.ext.assets import Environment, Bundle

from scratch.custom_filters import (
    datetime_filter, get_color_class, get_favorite_class
)


def create_app():
    from scratch.views import views
    from scratch import models

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
    models.db.init_app(app)
    app.register_blueprint(views)
    return app
