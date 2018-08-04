NewsDiffs
==========

A website and framework that tracks changes in online news articles over time.

Original installation at newsdiffs.org.
A product of the Knight Mozilla MIT news hackathon in June 2012.
Authors: Eric Price (ecprice@mit.edu), Greg Price (gnprice@gmail.com),
 and Jennifer 8. Lee (jenny@jennifer8lee.com)
Factotum: Carl Gieringer

This is free software under the MIT/Expat license; see LICENSE.
The project's source code lives at http://github.com/ecprice/newsdiffs .


Requirements
------------

You need to have installed on your local machine
* Git
* Python 2.6 or later
* Django and other Python libraries

On a Debian- or Ubuntu-based system, it may suffice (untested) to run
  $ sudo apt-get install git-core python-django python-django-south python-simplejson

On Mac OS, the easiest way may be to install pip:
  http://www.pip-installer.org/en/latest/installing.html
and then
  $ pip install Django


Initial setup
-------------

  $ python website/manage.py syncdb && python website/manage.py migrate
  $ mkdir articles


Running NewsDiffs Locally
-------------------------

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

 $ pip install beautifulsoup4 beautifulsoup html5lib

Note that we need two versions of BeautifulSoup, both 3.2 and 4.0;
some websites are parsed correctly in only one version.

Then run
  $ python website/manage.py scraper

This will populate the articles repository with a list of current news
articles.  This is a snapshot at a single time, so the website will
not yet have any changes. To get changes, wait some time (say, 3
hours) and run 'python website/manage.py scraper' again.  If any of
the articles have changed in the intervening time, the website should
display the associated changes.

The scraper will log progress to /tmp/newsdiffs_logging (which is
overwritten each run) and errors to /tmp/newsdiffs/logging_errs (which
is cumulative).

To run the scraper every hour, run something like:

 $ while true; do python website/manage.py scraper; sleep 60m; done

or make a cron job.

Adding new sites to the scraper
-------------------------------

The procedure for adding new sites to the scraper is outlined in
parsers/__init__.py .  You need to

  (1) Create a new parser module in parsers/ .  This should be a
      subclass of BaseParser (in parsers/baseparser.py).  Model it off
      the other parsers in that directory.  You can test the parser
      with by running, e.g.,

$ python parsers/test_parser.py bbc.BBCParser

      which will output a list of URLs to track, and

$ python parsers/test_parser.py bbc.BBCParser http://www.bbc.co.uk/news/uk-21649494

      which will output the text that NewsDiffs would store.

  (2) Add the parser to 'parsers' in parsers/__init__.py

This should cause the scraper to start tracking the site.

To make the source display properly on the website, you will need
minor edits to two other files: website/frontend/models.py and
website/frontend/views.py (to define the display name and create a tab
for the source, respectively).  Search for 'bbc' to find the locations
to edit.


Running MySQL locally
----------------------------------------------
```
$ docker run --name=mysql -p 3306:3306 -d mysql/mysql-server
# Look for GENERATED in the container output to find the auto-generated root password
$ docker log mysql | grep GENERATED
# Use the root password here
$ docker exec -it mysql mysql -uroot -p
Enter password:
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 13
Server version: 8.0.12

Copyright (c) 2000, 2018, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> ALTER USER 'root'@'localhost' IDENTIFIED BY 'new-root-password';
Query OK, 0 rows affected (0.10 sec)

mysql> CREATE USER 'newsdiffs'@'%' IDENTIFIED BY 'newsdiffs-password';
Query OK, 0 rows affected (0.02 sec)

mysql> GRANT ALL PRIVILEGES ON *.* TO 'newsdiffs'@'%' WITH GRANT OPTION;
Query OK, 0 rows affected, 1 warning (0.08 sec)

mysql> create database newsdiffs;
Query OK, 1 row affected (0.04 sec)

mysql> ^DBye
```

Copy `DATABASES` and `CACHES` from `settings_main.py` to `settings_dev.py`.  Update the password in `DATABASES` as 
necessary for whatever passwords you used above for the `newsdiffs` user.

```
$ PYTHONPATH=$(pwd) python website/manage.py syncdb
$ PYTHONPATH=$(pwd) python website/manage.py migrate
$ PYTHONPATH=$(pwd) python manage.py createcachetable cache_table
```

Load testing the app
--------------------

To put load on the system:

```
locust -f locustfile.py
```

Visit localhost:8089 and start a test.

To troubleshoot MySQL max_user_connections errors:

```
$ docker exec -it mysql mysql -uroot -p
mysql> -- throttle the number of connections so that it is easy to hit the limit
mysql> ALTER USER 'newsdiffs'@'%' WITH MAX_USER_CONNECTIONS 5;
mysql> -- this will show you the number of connections to the server
mysql> show status like '%connected%';
```
Start a locust swarm with 300 users at 100 users/second .  Keep refreshing http://127.0.0.1:8000/browse/
and you should eventually get something like:

> OperationalError at /browse/
>   (1226, "User 'newsdiffs' has exceeded the 'max_user_connections' resource (current value: 5)")

Now you have recreated the issue.