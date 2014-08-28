#! /bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$(dirname "$DIR")"
source sandbox/bin/activate
./manage.py worker update
./manage.py worker update_ted
./manage.py worker update_favourites
