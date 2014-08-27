ungm-scraper
============

System prerequisites
--------------------

These packages should be installed as superuser (root).


###Debian based systems###

Install these before setting up an environment:

    apt-get install python-setuptools python-dev python-virtualenv git

###RHEL based systems###

Install Python2.7: [https://gist.github.com/androane/8f0f7eb77824f63dd2f8](https://gist.github.com/androane/8f0f7eb77824f63dd2f8)

    yum install git


Product directory
-----------------

Create the product directory:

    mkdir -p /var/local/scratch
    mkdir /var/local/scratch/logs

Create a new user:

    adduser edw

Change the product directory's owner:

    chown edw:edw /var/local/scratch -R


Install dependencies
--------------------
We should use Virtualenv for isolated environments. The following commands will
be run as an unprivileged user in the product directory:

Clone the repository:

    git clone git@bitbucket.org:edw_pure/ungm-scraper.git

Create & activate a virtual environment:

    virtualenv --no-site-packages sandbox
    echo '*' > sandbox/.gitignore
    source sandbox/bin/activate

Install dependencies:

    pip install -r requirements-dep.txt

Create a configuration file:

    mkdir -p instance
    cp settings.py.example instance/settings.py

    # Follow instructions in instance/settings.py to adapt it to your needs.

To set up a configuration file run the following commands and look in settings.example 
for an settings example file:

    mkdir -p instance
    echo '*' >> instance/.gitignore
    touch instance/settings.py
    
Initialize the database:

    ./manage.py db init


Crontab job
-----------

To add a Crontab job for the current user type the following command:

    crontab -e
    
Add the following line to execute the script every day of the year at 00:00:

    00 00 * * * bash /var/local/scratch/scripts/scraper_commands.sh
    

Build production
----------------

Setup the production environment like this (using an unprivileged user):

    install dependencies, see above
    cd /var/local/scratch

Write a Crontab job as specified above.

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
notifications to all the addresses specified in settings by ``NOTIFY_EMAILS``

    ./manage.py worker update
    
    
### utils ###


Retrieve the tree of number codes generated by searching for a text string:

    ./manage.py utils search_unspscs -t software
    
The above command will retrieve all the codes associated with ``software``


Other Information
-----------------

The scraping process is wrapped in a try-except block. If the scraping process
fails for any reason(for example if the scraped website changes its layout), 
then an email containing the occured error and its location is sent to the
list of emails specified in settings by ``DEVELOEPRS_EMAILS``


Local Testing
-------------
The following steps will guide you on how to run the project against a local
python server serving HTML files. The served HTML files simulate the answers
received by interogating the live UNGM.


1.In a window terminal, run a simple HTTP Server with python to make local 
requests in the testing directory:
    
    cd testing/server/
    python -m SimpleHTTPServer 8080

Now open a new terminal window.

2.Initialize the DB.
    
    ./manage.py add add_tender 27501

3(optional). Add as many tenders as you wish in the database using management
commands and passing the filename argument. Examples:

    ./manage.py add add_tender 27501
    ./manage.py add add_tender 27954

Filenames must be chosen form the ones located at
testing/server/Public/Notice/*.html, excluding tender_notices.html

4(optional). Add as many winners as you wish in the database using management
commands and passing the filename argument. Examples:

    ./manage.py add add_winner 101104
    ./manage.py add add_winner 101119

Filenames must be chosen form the ones located at
testing/server/Public/ContractAward/*.html, excluding contract_winners.html

5.Run the following command to scrap and find the new tenders and then adding
them to the DB:

    ./manage.py worker update

5.Run the server:

    ./manage.py runserver

Access it at: `http://localhost:5000/tenders/`

6(optional). Feel free to close the first terminal which was running the python
simple HTTP server.


CONTACTS
--------

People involved in this project are:

+ Cornel Nit (cornel.nitu at eaudeweb.ro)
+ Alex Eftimie (alex.eftimie at eaudeweb.ro)
+ Iulia Chriac (iulia.chiriac at eaudeweb.ro)
+ Mihai Zamfir (mihai.zamfir at eaudeweb.ro)
