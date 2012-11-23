#!/usr/bin/python

import urllib2
from BeautifulSoup import BeautifulSoup
from StringIO import StringIO
from datetime import datetime, timedelta
import dateutil.parser
import subprocess

WEBSITE = 'http://www.newsdiffs.org/browse/'
if datetime.now().hour < 8: #Overnight, less frequent updates
    MAX_TIME = timedelta(minutes=120)
else:
    MAX_TIME = timedelta(minutes=60)
    
EMAILS = 'ecprice@mit.edu jenny8lee@gmail.com price@mit.edu'.split()

def send_alert_email(subject, body):
    email = 'Subject: %s\n\n%s' % (subject, body)

    p = subprocess.Popen(['/usr/bin/msmtp', '-t'] + EMAILS,
                         stdin=subprocess.PIPE)
    p.communicate(email)
    if p.wait():
        print 'Bad return code:', p.returncode


def get_update_time():
    html = urllib2.urlopen(WEBSITE)
    soup = BeautifulSoup(html)
    datestr = soup.findAll('td')[1].getText()
    datestr = datestr.replace('midnight', '12:00am').replace('noon', '12:00pm')
    try:
        date = dateutil.parser.parse(datestr)
    except ValueError:
        print datestr
        raise
    return date

if __name__ == '__main__':
    try:
        update_time = get_update_time()
        time_since_update = datetime.now() - update_time
        print 'Update time:', time_since_update
        if time_since_update > MAX_TIME:
            send_alert_email('Trouble with newsdiffs.org',
                             'No updates since %s\n%s is too long' %
                             (update_time, time_since_update))
    except Exception, e:
        import traceback
        traceback.print_exc()
        send_alert_email('Trouble with newsdiffs.org',
                         'Cannot check website\n%s' % traceback.format_exc())

