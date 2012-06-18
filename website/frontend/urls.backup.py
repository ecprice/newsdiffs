from django.conf.urls.defaults import *

urlpatterns = patterns('',
  #
  (r'^diffview', 'frontend.views.diffview'),
  (r'^view', 'frontend.views.view'),
  (r'^', 'frontend.views.index'),
)
