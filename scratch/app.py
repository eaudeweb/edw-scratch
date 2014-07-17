from flask import Flask


def create_app():
    from scratch.views import views
    from scratch import models

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('settings')
    models.db.init_app(app)
    app.register_blueprint(views)
    return app
