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


Running for yourself
--------------------

Do the initial setup above.  Then to start the webserver for testing:
  $ python website/manage.py runserver


Running the scraper
-------------------

Do the initial setup above.  You will also need additional Python
libraries; on a Debian- or Ubuntu-based system, it may suffice
(untested) to run
  $ sudo apt-get install python-bs4

Then run
  $ python scraper.py
