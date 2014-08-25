from django.conf.urls import url

urlpatterns = [
  # These are deprecated, and meant to preserve legacy URLs:
  url(r'^diffview/$', 'frontend.views.old_diffview'),
  url(r'^article-history/$', 'frontend.views.article_history', name='article_history'),

  # These are current:
  url(r'^upvote/$', 'frontend.views.upvote', name='upvote'),
  url(r'^diff/(?P<vid1>\d+)/(?P<vid2>\d+)/(?P<urlarg>.*)$', 'frontend.views.diffview', name='diffview'),
  url(r'^about/$', 'frontend.views.about', name='about'),
  url(r'^browse/$', 'frontend.views.browse', name='browse'),
  url(r'^browse/(.*)$', 'frontend.views.browse', name='browse'),
  url(r'^feed/browse/(.*)$', 'frontend.views.feed', name='feed'),
  url(r'^contact/$', 'frontend.views.contact', name='contact'),
  url(r'^examples/$', 'frontend.views.examples', name='examples'),
  url(r'^subscribe/$', 'frontend.views.subscribe', name='subscribe'),
  url(r'^press/$', 'frontend.views.press', name='press'),
  url(r'^feed/article-history/(.*)$', 'frontend.views.article_history_feed', name='article_history_feed'),
  url(r'^article-history/(?P<urlarg>.*)$', 'frontend.views.article_history', name='article_history'),
  url(r'^json/view/(?P<vid>\d+)/?$', 'frontend.views.json_view'),
  url(r'^$', 'frontend.views.front', name='root'),
]
