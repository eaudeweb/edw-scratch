from flask import Flask
from scratch.models import Tender, TenderDocument, Winner
import flask.ext.whooshalchemy as whooshalchemy


def create_app():
    from scratch.views import views
    from scratch import models

    app = Flask(__name__, instance_relative_config=True)
    whooshalchemy.whoosh_index(app, Tender)
    whooshalchemy.whoosh_index(app, TenderDocument)
    whooshalchemy.whoosh_index(app, Winner)
    app.config.from_pyfile('settings.py')
    models.db.init_app(app)
    app.register_blueprint(views)
    return app
