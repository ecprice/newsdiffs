from django.conf.urls import url

urlpatterns = [
  # These are deprecated, and meant to preserve legacy URLs:
  url(r'^diffview/$', 'frontend.views.old_diffview'),
  url(r'^article-history/$', 'frontend.views.article_history', name='article_history'),

  # These are current:
  url(r'^diff/(?P<vid1>\d+)/(?P<vid2>\d+)/(?P<urlarg>.*)$', 'frontend.views.diffview', name='diffview'),
  url(r'^about/$', 'frontend.views.about', name='about'),
  url(r'^entdecken/$', 'frontend.views.entdecken', name='entdecken'),
  url(r'^kontakt/$', 'frontend.views.kontakt', name='kontakt'),
  url(r'^impressum/$', 'frontend.views.impressum', name='impressum'),
  url(r'^browse/$', 'frontend.views.browse', name='browse'),
  url(r'^artikel/$', 'frontend.views.artikel', name='artikel'),
  url(r'^history/$', 'frontend.views.history', name='history'),
  url(r'^suchergebnisse/$', 'frontend.views.suchergebnisse', name='suchergebnisse'),
  url(r'^browse/(.*)$', 'frontend.views.browse', name='browse'),
  url(r'^feed/browse/(.*)$', 'frontend.views.feed', name='feed'),
  url(r'^highlights/$', 'frontend.views.highlights', name='highlights'),
  url(r'^feed/article-history/(.*)$', 'frontend.views.article_history_feed', name='article_history_feed'),
  url(r'^article-history/(?P<urlarg>.*)$', 'frontend.views.article_history', name='article_history'),
  url(r'^json/view/(?P<vid>\d+)/?$', 'frontend.views.json_view'),
  url(r'^$', 'frontend.views.index', name='root'),
]
