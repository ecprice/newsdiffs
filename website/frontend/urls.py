from django.conf.urls import url
from . import views

urlpatterns = [
  # These are deprecated, and meant to preserve legacy URLs:
  url(r'^diffview/$', views.old_diffview),
  url(r'^article-history/$', views.article_history, name='article_history'),

  # These are current:
  url(r'^upvote/$', views.upvote, name='upvote'),
  url(r'^diff/(?P<vid1>\d+)/(?P<vid2>\d+)/(?P<urlarg>.*)$', views.diffview, name='diffview'),
  url(r'^about/$', views.about, name='about'),
  url(r'^browse/$', views.browse, name='browse'),
  url(r'^browse/(.*)$', views.browse, name='browse'),
  url(r'^feed/browse/(.*)$', views.feed, name='feed'),
  url(r'^contact/$', views.contact, name='contact'),
  url(r'^examples/$', views.examples, name='examples'),
  url(r'^subscribe/$', views.subscribe, name='subscribe'),
  url(r'^press/$', views.press, name='press'),
  url(r'^feed/article-history/(.*)$', views.article_history_feed, name='article_history_feed'),
  url(r'^article-history/(?P<urlarg>.*)$', views.article_history, name='article_history'),
  url(r'^json/view/(?P<vid>\d+)/?$', views.json_view),
  url(r'^$', views.front, name='root'),
]
