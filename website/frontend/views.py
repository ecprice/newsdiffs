import datetime
import re

from django.shortcuts import render_to_response, get_object_or_404, redirect
from models import Article, Version
import models
import json
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
import urllib
import django.db
import time
from django.template import Context, RequestContext, loader
from django.views.decorators.cache import cache_page

OUT_FORMAT = '%B %d, %Y at %l:%M%P EDT'

SEARCH_ENGINES = """
http://www.ask.com
http://www.google
https://www.google
search.yahoo.com
http://www.bing.com
""".split()

def came_from_search_engine(request):
    return any(x in request.META.get('HTTP_REFERER', '')
               for x in SEARCH_ENGINES)



def Http400():
    t = loader.get_template('404.html')
    return HttpResponse(t.render(Context()), status=400)

def get_first_update(source):
    if source is None:
        source = ''
    updates = models.Article.objects.order_by('last_update').filter(last_update__gt=datetime.datetime(1990, 1, 1, 0, 0),
                                                                    url__contains=source)
    try:
        return updates[0].last_update
    except IndexError:
        return datetime.datetime.now()

def get_last_update(source):
    if source is None:
        source = ''
    updates = models.Article.objects.order_by('-last_update').filter(last_update__gt=datetime.datetime(1990, 1, 1, 0, 0), url__contains=source)
    try:
        return updates[0].last_update
    except IndexError:
        return datetime.datetime.now()

def get_articles(source=None, distance=0):
    articles = []
    rx = re.compile(r'^https?://(?:[^/]*\.)%s/' % source if source else '')

    pagelength = datetime.timedelta(days=1)
    end_date = datetime.datetime.now() - distance * pagelength
    start_date = end_date - pagelength

    print 'Asking query'
    version_query = '''SELECT
    version.id, version.article_id, version.v, version.title,
      version.byline, version.date, version.boring, version.diff_json,
      T.age as age,
      Articles.url as a_url, Articles.initial_date as a_initial_date,
      Articles.last_update as a_last_update, Articles.last_check as a_last_check
    FROM version,
     (SELECT Articles.id as article_id, MAX(T3.date) AS age, COUNT(T3.id) AS num_vs
      FROM Articles LEFT OUTER JOIN version T3 ON (Articles.id = T3.article_id)
      WHERE (T3.boring=0) GROUP BY Articles.id
      HAVING (age > %s  AND age < %s  AND num_vs > 1 )) T, Articles
    WHERE (version.article_id = Articles.id) and
          (version.article_id = T.article_id) and
          NOT version.boring
    ORDER BY date'''

    all_versions = models.Version.objects.raw(version_query,
                                              (start_date, end_date))
    article_dict = {}
    for v in all_versions:
        a=models.Article(id=v.article_id,
                         url=v.a_url, initial_date=v.a_initial_date,
                         last_update=v.a_last_update, last_check=v.a_last_check)
        v.article = a
        article_dict.setdefault(v.article, []).append(v)

    for article, versions in article_dict.items():
        url = article.url
        if not rx.match(url):
            print 'REJECTING', url
            continue
        if 'blogs.nytimes.com' in url: #XXX temporary
            continue

        if len(versions) < 2:
            continue
        rowinfo = get_rowinfo(article, versions)
        articles.append((article, versions[-1], rowinfo))
    print 'Queries:', len(django.db.connection.queries), django.db.connection.queries
    articles.sort(key = lambda x: x[-1][0][1].date, reverse=True)
    return articles


SOURCES = '''nytimes.com cnn.com politico.com washingtonpost.com
bbc.co.uk'''.split()

def is_valid_domain(domain):
    """Cheap method to tell whether a domain is being tracked."""
    return any(domain.endswith(source) for source in SOURCES)

@cache_page(60 * 30)  #30 minute cache
def browse(request, source=''):
    if source not in SOURCES + ['']:
        raise Http404
    pagestr=request.REQUEST.get('page', '1')
    try:
        page = int(pagestr)
    except ValueError:
        page = 1

    first_update = get_first_update(source)
    num_pages = (datetime.datetime.now() - first_update).days + 1
    page_list=range(1, 1+num_pages)

    articles = get_articles(source=source, distance=page-1)
    return render_to_response('browse.html', {
            'source': source, 'articles': articles,
            'page':page,
            'page_list': page_list,
            'first_update': first_update,
            'sources': SOURCES
            })

@cache_page(60 * 30)  #30 minute cache
def feed(request, source=''):
    if source not in SOURCES + ['']:
        raise Http404
    pagestr=request.REQUEST.get('page', '1')
    try:
        page = int(pagestr)
    except ValueError:
        page = 1

    first_update = get_first_update(source)
    last_update = get_last_update(source)
    num_pages = (datetime.datetime.now() - first_update).days + 1
    page_list=range(1, 1+num_pages)

    articles = get_articles(source=source, distance=page-1)
    return render_to_response('feed.xml', {
            'source': source, 'articles': articles,
            'page':page,
            'request':request,
            'page_list': page_list,
            'last_update': last_update,
            'sources': SOURCES
            },
            context_instance=RequestContext(request),
            mimetype='application/atom+xml')

def old_diffview(request):
    """Support for legacy diff urls"""
    url = request.REQUEST.get('url')
    v1tag = request.REQUEST.get('v1')
    v2tag = request.REQUEST.get('v2')
    if url is None or v1tag is None or v2tag is None:
        return HttpResponseRedirect(reverse(front))

    try:
        v1 = Version.objects.get(v=v1tag)
        v2 = Version.objects.get(v=v2tag)
    except Version.DoesNotExist:
        return Http400()

    try:
        article = Article.objects.get(url=url)
    except Article.DoesNotExist:
        return Http400()

    return redirect(reverse('diffview', kwargs=dict(vid1=v1.id,
                                                    vid2=v2.id,
                                                    urlarg=article.filename())),
                    permanent=True)


def diffview(request, vid1, vid2, urlarg):
    # urlarg is unused, and only for readability
    # Could be strict and enforce urlarg == article.filename()
    try:
        v1 = Version.objects.get(id=int(vid1))
        v2 = Version.objects.get(id=int(vid2))
    except Version.DoesNotExist:
        raise Http404

    article = v1.article

    if v1.article != v2.article:
        raise Http404

    title = article.latest_version().title

    versions = dict(enumerate(article.versions()))

    adjacent_versions = []
    dates = []
    texts = []

    for v in (v1, v2):
        texts.append(v.text())
        dates.append(v.date.strftime(OUT_FORMAT))

        indices = [i for i, x in versions.items() if x == v]
        if not indices:
            #One of these versions doesn't exist / is boring
            return Http400()
        index = indices[0]
        adjacent_versions.append([versions.get(index+offset)
                                  for offset in (-1, 1)])


    if any(x is None for x in texts):
        return Http400()

    links = []
    for i in range(2):
        if all(x[i] for x in adjacent_versions):
            diffl = reverse('diffview', kwargs=dict(vid1=adjacent_versions[0][i].id,
                                                    vid2=adjacent_versions[1][i].id,
                                                    urlarg=article.filename()))
            links.append(diffl)
        else:
            links.append('')

    return render_to_response('diffview.html', {
            'title': title,
            'date1':dates[0], 'date2':dates[1],
            'text1':texts[0], 'text2':texts[1],
            'prev':links[0], 'next':links[1],
            'article_shorturl': article.filename(),
            'article_url': article.url, 'v1': v1, 'v2': v2,
            'display_search_banner': came_from_search_engine(request),
            })

def get_rowinfo(article, version_lst=None):
    if version_lst is None:
        version_lst = article.versions()
    rowinfo = []
    lastv = None
    urlarg = article.filename()
    for version in version_lst:
        date = version.date
        if lastv is None:
            diffl = ''
        else:
            diffl = reverse('diffview', kwargs=dict(vid1=lastv.id,
                                                    vid2=version.id,
                                                    urlarg=urlarg))
        rowinfo.append((diffl, version))
        lastv = version
    rowinfo.reverse()
    return rowinfo


def prepend_http(url):
    """Return a version of the url that starts with the proper scheme.

    url may look like

    www.nytimes.com
    https:/www.nytimes.com    <- because double slashes get stripped
    http://www.nytimes.com
    """
    components = url.split('/', 2)
    if len(components) <= 2 or '.' in components[0]:
        components = ['http:', '']+components
    elif components[1]:
        components[1:1] = ['']
    return '/'.join(components)


def article_history(request, urlarg=''):
    url = request.REQUEST.get('url') # this is the deprecated interface.
    if url is None:
        url = urlarg
    if len(url) == 0:
        return HttpResponseRedirect(reverse(front))

    url = url.split('?')[0]  #For if user copy-pastes from news site

    url = prepend_http(url)

    # This is a hack to deal with unicode passed in the URL.
    # Otherwise gives an error, since our table character set is latin1.
    url = url.encode('ascii', 'ignore')

    # Give an error on urls with the wrong hostname without hitting the
    # database.  These queries are usually spam.
    domain = url.split('/')[2]
    if not is_valid_domain(domain):
        return render_to_response('article_history_missing.html', {'url': url})


    try:
        article = Article.objects.get(url=url)
    except Article.DoesNotExist:
        try:
            return render_to_response('article_history_missing.html', {'url': url})
        except (TypeError, ValueError):
            # bug in django + mod_rewrite can cause this. =/
            return HttpResponse('Bug!')

    if len(urlarg) == 0:
        return HttpResponseRedirect(reverse(article_history, args=[article.filename()]))

    rowinfo = get_rowinfo(article)
    return render_to_response('article_history.html', {'article':article,
                                                       'versions':rowinfo,
            'display_search_banner': came_from_search_engine(request),
                                                       })
def article_history_feed(request, url=''):
    url = prepend_http(url)
    article = get_object_or_404(Article, url=url)
    rowinfo = get_rowinfo(article)
    return render_to_response('article_history.xml',
                              { 'article': article,
                                'versions': rowinfo,
                                'request': request,
                                },
                              context_instance=RequestContext(request),
                              mimetype='application/atom+xml')

def json_view(request, vid):
    version = get_object_or_404(Version, id=int(vid))
    data = dict(
        title=version.title,
        byline = version.byline,
        date = version.date.isoformat(),
        text = version.text(),
        )
    return HttpResponse(json.dumps(data), mimetype="application/json")

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
    return render_to_response('front.html', {'sources': SOURCES})

def subscribe(request):
    return render_to_response('subscribe.html', {})

def press(request):
    return render_to_response('press.html', {})

