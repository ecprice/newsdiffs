import os
from django.conf.urls import include, url
from django.views.generic import RedirectView

from frontend import urls

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
  url(r'^(assets/ico/)?favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico')),
  url(r'^robots.txt$', RedirectView.as_view(url='/static/robots.txt')),
  url(r'^', include(urls)),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', admin.site.root),
]
