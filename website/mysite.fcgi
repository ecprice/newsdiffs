#!/usr/bin/python
import sys, os

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)

# Add a custom Python path.
sys.path.insert(0, os.path.dirname(ROOT_DIR))
sys.path.insert(0, ROOT_DIR)

# Switch to the directory of your project. (Optional.)
# os.chdir("/home/user/myproject")

# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ['DJANGO_SETTINGS_MODULE'] = "website.settings"

from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false")
