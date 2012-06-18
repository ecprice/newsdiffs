import os
from django.conf.urls.defaults import *
from django.conf.urls.static import static

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
   url(r'^newsdiffer/static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': ROOT_DIR+'/website/static',
        }),
   (r'^newsdiffer/', include('newsdiffer.frontend.urls')),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', admin.site.root),
)
