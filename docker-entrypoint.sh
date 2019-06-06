#!/bin/bash

COMMANDS="shell utils db sync runserver api match"

while ! nc -z mysql 3306; do
  echo "Waiting for MySQL server at 'mysql' to accept connections on port 3306..."
  sleep 3s
done

#create database for service
if ! mysql -h mysql -u root -p$MYSQL_ROOT_PASSWORD -e "use $MYSQL_DATABASE;"; then
  echo "CREATE DATABASE $MYSQL_DATABASE"
  mysql -h mysql -u root -p$MYSQL_ROOT_PASSWORD -e "CREATE DATABASE $MYSQL_DATABASE CHARACTER SET utf8 COLLATE utf8_general_ci;"
  mysql -h mysql -u root -p$MYSQL_ROOT_PASSWORD -e "CREATE USER '$MYSQL_DATABASE'@'%' IDENTIFIED BY '$MYSQL_PASSWORD';"
  mysql -h mysql -u root -p$MYSQL_ROOT_PASSWORD -e "GRANT ALL PRIVILEGES ON $MYSQL_DATABASE.* TO '$MYSQL_USER'@'%';"
fi


if [ ! -e .skip-db-init ]; then
  touch .skip-db-init
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
