newsdiffs
==========

A website and framework that tracks changes in online news articles over time.


Initial setup
-------------

  $ python models.py -s
  $ python website/manage.py syncdb
  $ git init articles
  $ cd articles && touch x && git add x && git commit -m 'Initial commit'

You will need Django installed, and other libraries.  On a Debian- or
Ubuntu-based system, it may suffice (untested) to run
  $ sudo apt-get install python-django python-simplejson

On Mac OS, the easiest way may be to install pip:
  http://www.pip-installer.org/en/latest/installing.html
and then
  $ pip install Django


Running for yourself
--------------------

Do the initial setup above.  Then to start the webserver for testing:
  $ python website/manage.py runserver

and visit http://localhost:8000/

Running the scraper
-------------------

Do the initial setup above.  You will also need additional Python
libraries; on a Debian- or Ubuntu-based system, it may suffice
(untested) to run
  $ sudo apt-get install python-bs4 python-beautifulsoup

on a Mac, you will want something like

 $ pip install beautifulsoup4
 $ pip install beautifulsoup
 $ pip install html5lib

Note that we need two versions of BeautifulSoup, both 3.2 and 4.0;
some websites are parsed correctly in only one version.

Then run
  $ python scraper.py

This will populate the articles repository with a list of current news
articles.  This is a snapshot at a single time, so the website will
not yet have any changes. To get changes, wait some time (say, 3
hours) and run 'python scraper.py' again.  If any of the articles have
changed in the intervening time, the website should display the
associated changes.

To run the scraper every hour, run something like:

 $ while true; do python scraper.py; sleep 60m; done
