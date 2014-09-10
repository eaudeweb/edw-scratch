#!/usr/bin/env python

from scratch.app import create_app
from scratch.manager import create_manager


app = create_app()


if __name__ == '__main__':
    try:
        create_manager(app).run()
        assert False
    except:
        if app.config['DEBUG']:
            raise
        else:
            from raven import Client
            client = Client(app.config.get('SENTRY_DSN'))
            client.captureException()
