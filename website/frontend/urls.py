from django.conf.urls.defaults import *

urlpatterns = patterns('',
  #
  (r'^upvote', 'frontend.views.upvote'),
  (r'^diffview', 'frontend.views.diffview'),
  (r'^view', 'frontend.views.view'),
  (r'^about', 'frontend.views.about'),
  (r'^browse', 'frontend.views.browse'),
  (r'^contact', 'frontend.views.contact'),
  (r'^subscribe', 'frontend.views.subscribe'),
  (r'^examples', 'frontend.views.examples'),
  (r'^press', 'frontend.views.press'),
  (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/static/images/favicon.ico'}),
  (r'^assets/ico/favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/static/images/favicon.ico'}),
  (r'^$', 'frontend.views.front'),
)
