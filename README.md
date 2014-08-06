ungm-scraper
============


Install dependencies
--------------------
We should use Virtualenv for isolated environments. The following commands will
be run as an unprivileged user in the product directory:

Clone the repository::

    git clone git@bitbucket.org:edw_pure/ungm-scraper.git

Create & activate a virtual environment:

    virtualenv --no-site-packages sandbox
    echo '*' > sandbox/.gitignore
    source sandbox/bin/activate

Install dependencies:

    pip install -r requirements-dev.txt


Create a configuration file:

To set up a configuration file run the following commands and look in settings.example 
for an settings example file:

    mkdir -p instance
    echo '*' >> instance/.gitignore
    touch instance/settings.py


Management commands
-------------------

### db ###


Initialize the database:

    ./manage.py db init

### scrap ###


Parse a tenders list html and display the output:

    ./manage.py scrap parse_tenders_list_html

Parse a winners list html and display the output:

    ./manage.py scrap parse_winners_list_html

Parse a tender html and display the output:

    ./manage.py scrap parse_tender_html 27501

Parse a winner html and display the output:

    ./manage.py scrap parse_winner_html 101104


### worker ###


Check for new available tenders. Save them into the DB and send email
notifications to all the addresses specified in settings['NOTIFY_EMAILS']

    ./manage.py worker update

...

Run a local server:

    ./manage.py runserver


Tests
-----

Run a simple HTTP Server with python to make local requests in the testing
directory:

    cd testing/server/
    python -m SimpleHTTPServer 8080

Add some tenders in the database using management commands and passing the
filename argument:

    ./manager.py add add_tender 27501
    ./manager.py add add_tender 27954

Add some tenders in the database using management commands and passing the
filename argument:

    ./manager.py add add_winner 101104
    ./manager.py add add_winner 101119