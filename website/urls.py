from django.conf.urls.defaults import *
from django.conf.urls.static import static

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
   url(r'^newsdiffer/static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': '/mit/ecprice/web_scripts/newsdiffer/static',
        }),
   (r'^newsdiffer/', include('website.frontend.urls')),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', admin.site.root),
)
