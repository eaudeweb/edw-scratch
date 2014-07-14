#!/usr/bin/env python

from scratch.app import create_app
from scratch.manager import create_manager


app = create_app()


if __name__ == '__main__':
    create_manager(app).run()
