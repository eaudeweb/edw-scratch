ungm-scraper
============


Install dependencies
--------------------
We should use Virtualenv for isolated environments. The following commands will
be run as an unprivileged user in the product directory::

1. Clone the repository::

    git clone git@bitbucket.org:edw_pure/ungm-scraper.git

2. Create & activate a virtual environment::

    virtualenv --no-site-packages sandbox
    echo '*' > sandbox/.gitignore
    source sandbox/bin/activate

3. Install dependencies::

    pip install -r requirements-dev.txt


4. Create a configuration file::

To set up a configuration file run the following commands and look in
settings.example for an settings example file::

    mkdir -p instance
    echo '*' >> instance/.gitignore
    touch instance/settings.py


Management commands
-------------------

Parse a tender html and display the output:

 ./manage.py parse_tender_html download/test.html

...

Run a local server:

 ./manage.py runserver


Tests
-----

1. Run a simple HTTP Server with python to make local requests in the testing
directory:

    cd testing/server/
    python -m SimpleHTTPServer 8080

2. Add some tenders in the database using management commands and passing the
filename argument:

    ./manager.py add add_tender 27501
    ./manager.py add add_tender 27954

3. Add some tenders in the database using management commands and passing the
filename argument:

    ./manager.py add add_winner 101104
    ./manager.py add add_winner 101119
