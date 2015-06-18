import os
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.views.generic import RedirectView

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
   url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': ROOT_DIR+'/website/static',
        }, name='static'),
  url(r'^(assets/ico/)?favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico')),
  url(r'^robots.txt$', RedirectView.as_view(url='/static/robots.txt')),
  url(r'^', include('website.frontend.urls')),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', admin.site.root),
]
