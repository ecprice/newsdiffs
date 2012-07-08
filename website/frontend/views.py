import datetime
import re

from django.shortcuts import render_to_response, get_object_or_404
from models import Article, Version
import models
import simplejson
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
import urllib
import django.db

OUT_FORMAT = '%B %d, %Y at %l:%M%P EDT'

def num_browse_pages(source):
    if source is None:
        source = ''
    first_update = models.Article.objects.order_by('last_update').filter(last_update__gt=datetime.datetime(1990, 1, 1, 0, 0),
                                                                         url__contains=source)[0].last_update
    num_pages = (datetime.datetime.now() - first_update).days + 1
    return num_pages

def get_articles(source=None, distance=0):
    articles = []
    rx = re.compile(r'^https?://(?:[^/]*\.)%s/' % source if source else '')

    pagelength = datetime.timedelta(days=1)
    end_date = datetime.datetime.now() - distance * pagelength
    start_date = end_date - pagelength


    all_versions = models.Version.objects.annotate(num_vs=models.models.Count('article__version')).filter(num_vs__gt=1, article__version__boring=False, article__last_update__gt=start_date, article__last_update__lt=end_date).order_by('date').select_related()
    print 'Queries:', len(django.db.connection.queries), django.db.connection.queries
    print 'sql responded'
    article_dict = {}
    for version in all_versions:
        article_dict.setdefault(version.article, []).append(version)

    for article, versions in article_dict.items():
        url = article.url
        if not rx.match(url):
            print 'REJECTING', url
            continue
        if 'blogs.nytimes.com' in url: #XXX temporary
            continue
        elif 'editions.cnn.com' in url:
            continue

        if len(versions) < 2:
            continue
        rowinfo = get_rowinfo(article, versions)
        articles.append((article, versions[-1], rowinfo))
    print 'Queries:', len(django.db.connection.queries), django.db.connection.queries
    articles.sort(key = lambda x: x[-1][0][1].date, reverse=True)
    return articles


SOURCES = set('nytimes.com cnn.com politico.com'.split() + [None])

def browse(request, source=None):
    if source not in SOURCES:
        raise Http404
    page=int(request.REQUEST.get('page', '1'))
    page_list=range(1, 1+num_browse_pages(source))
    articles = get_articles(source=source, distance=page-1)
    return render_to_response('browse_source.html', {
            'source': source, 'articles': articles,
            'page':page,
            'page_list': page_list,})


def diffview(request):
    url = request.REQUEST.get('url')
    v1tag = request.REQUEST.get('v1')
    v2tag = request.REQUEST.get('v2')

    v1 = Version.objects.get(v=v1tag)
    v2 = Version.objects.get(v=v2tag)
    article = Article.objects.get(url=url)
    assert(v1.article == article)
    assert(v2.article == article)

    title = article.latest_version().title

    versions = dict(enumerate(article.versions()))

    adjacent_versions = []
    dates = []
    texts = []

    for v in (v1, v2):
        texts.append(v.text())
        dates.append(v.date.strftime(OUT_FORMAT))

        index = [i for i, x in versions.items() if x == v][0]
        adjacent_versions.append([versions.get(index+offset)
                                  for offset in (-1, 1)])


    links = []
    for i in range(2):
        if all(x[i] for x in adjacent_versions):
            links.append('%s?%s' % (reverse(diffview),
                                    urllib.urlencode(dict(url=url,
                                                          v1=adjacent_versions[0][i].v,
                                                          v2=adjacent_versions[1][i].v,))))
        else:
            links.append('')

    return render_to_response('diffview.html', {
            'title': title,
            'date1':dates[0], 'date2':dates[1],
            'text1':texts[0], 'text2':texts[1],
            'prev':links[0], 'next':links[1],
            'article_url': url, 'v1': v1, 'v2': v2,
            })

def get_rowinfo(article, version_lst=None):
    if version_lst is None:
        version_lst = article.versions()
    rowinfo = []
    lastcommit = None
    for version in version_lst:
        date = version.date
        commit = version.v
        if lastcommit is None:
            diffl = ''
        else:
            diffl = '%s?%s' % (reverse(diffview),
                               urllib.urlencode(dict(url=article.url,
                                                     v1=lastcommit,
                                                     v2=commit)))
        rowinfo.append((diffl, version))
        lastcommit = commit
    rowinfo.reverse()
    return rowinfo

def article_history(request):
    url = request.REQUEST.get('url')
    article = Article.objects.get(url=url)
    rowinfo = get_rowinfo(article)
    return render_to_response('article_history.html', {'article':article,
                                                       'versions':rowinfo})

def upvote(request):
    article_url = request.REQUEST.get('article_url')
    diff_v1 = request.REQUEST.get('diff_v1')
    diff_v2 = request.REQUEST.get('diff_v2')
    remote_ip = request.META.get('REMOTE_ADDR')
    article_id = Article.objects.get(url=article_url).id
    models.Upvote(article_id=article_id, diff_v1=diff_v1, diff_v2=diff_v2, creation_time=datetime.datetime.now(), upvoter_ip=remote_ip).save()
    return render_to_response('upvote.html')

def about(request):
    return render_to_response('about.html', {})

def examples(request):
    return render_to_response('examples.html', {})

def contact(request):
    return render_to_response('contact.html', {})

def front(request):
    return render_to_response('front.html', {})

def subscribe(request):
    return render_to_response('subscribe.html', {})

def press(request):
    return render_to_response('press.html', {})

