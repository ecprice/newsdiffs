from django.conf.urls.defaults import *

urlpatterns = patterns('',
  #
  (r'^upvote', 'frontend.views.upvote'),
  (r'^diffview', 'frontend.views.diffview'),
  (r'^view', 'frontend.views.view'),
  (r'^about', 'frontend.views.about'),
  (r'^browse', 'frontend.views.browse'),
  (r'^contact', 'frontend.views.contact'),
  (r'^examples', 'frontend.views.examples'),
  (r'^$', 'frontend.views.front'),
)
