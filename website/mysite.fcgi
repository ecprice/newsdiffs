#!/usr/bin/python
import sys, os

DIR='/mit/ecprice/web_scripts'

# Add a custom Python path.
sys.path.insert(0, DIR)
sys.path.insert(0, DIR+"/newsdiffer")

# Switch to the directory of your project. (Optional.)
# os.chdir("/home/user/myproject")

# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ['DJANGO_SETTINGS_MODULE'] = "newsdiffer.settings"

from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false")
