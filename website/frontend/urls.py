from django.conf.urls.defaults import *

urlpatterns = patterns('',
  #
  url(r'^upvote/$', 'frontend.views.upvote', name='upvote'),
  url(r'^diffview/$', 'frontend.views.old_diffview'),
  url(r'^diff/(?P<vid1>\d+)/(?P<vid2>\d+)/(?P<urlarg>.*)$', 'frontend.views.diffview', name='diffview'),
  url(r'^about/$', 'frontend.views.about', name='about'),
  url(r'^browse/$', 'frontend.views.browse', name='browse'),
  url(r'^browse/(.*)$', 'frontend.views.browse', name='browse'),
  url(r'^contact/$', 'frontend.views.contact', name='contact'),
  url(r'^examples/$', 'frontend.views.examples', name='examples'),
  url(r'^subscribe/$', 'frontend.views.subscribe', name='subscribe'),
  url(r'^press/$', 'frontend.views.press', name='press'),
  url(r'^article-history/$', 'frontend.views.article_history', name='article_history'),
  url(r'^$', 'frontend.views.front', name='root'),
)
