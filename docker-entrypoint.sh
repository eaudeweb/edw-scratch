#!/bin/bash

COMMANDS="shell utils db sync runserver api match"

while ! nc -z mysql 3306; do
  echo "Waiting for MySQL server at 'mysql' to accept connections on port 3306..."
  sleep 3s
done

if [ "x$INIT_DB" = 'xyes' ]; then
  echo "Running DB CMD: ./manage.py db init"
  python manage.py db init
fi

if [ -z "$1" ]; then
  echo "Serving on port 5000"
  exec python manage.py runserver -h 0.0.0.0 -p 5000
fi

if [[ $COMMANDS == *"$1"* ]]; then
  exec python manage.py "$@"
fi

exec "$@"
