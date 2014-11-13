#!/usr/bin/env python

from scratch.app import create_app
from scratch.manager import create_manager


app = create_app()


if __name__ == '__main__':
    try:
        create_manager(app).run()
    except Exception as e:
        if app.config['DEBUG']:
            raise
        else:
            if isinstance(e, SystemExit) and e.code == 0:
                pass
            else:
                from raven import Client
                client = Client(app.config.get('SENTRY_DSN'))
                client.captureException()
