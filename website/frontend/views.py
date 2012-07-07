import datetime
import re

from django.shortcuts import render_to_response, get_object_or_404
from models import Article
import models
import simplejson
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
import urllib

OUT_FORMAT = '%B %d, %Y at %l:%M%P EDT'

def browse(request):
    articles = []
    models._refresh_metadata()
    for article in Article.objects.all():
        url = article.url
        if 'blogs.nytimes.com' in url: #XXX temporary
            continue
        elif 'editions.cnn.com' in url:
            continue
        vs = article.versions()
        if len(vs) < 2:
            continue
        rowinfo = []
        lastcommit = None
        for date, commit in vs:
            if lastcommit is None:
                diffl = ''
            else:
                diffl = '%s?%s' % (reverse(diffview),
                                   urllib.urlencode(dict(url=url, v1=lastcommit, v2=commit)))

            link = '%s?%s' % (reverse(view),
                               urllib.urlencode(dict(url=url, v=commit)))
            rowinfo.append((link, diffl, date))
            lastcommit = commit
        rowinfo.reverse()
        md = article.metadata()
        articles.append((url, md, len(vs), rowinfo))
    articles.sort(key = lambda x: (x[-2] > 1, x[-1][0][2]), reverse=True)
    return render_to_response('browse.html', {'articles': articles})


def diffview(request):
    url = request.REQUEST.get('url')
    v1 = request.REQUEST.get('v1')
    v2 = request.REQUEST.get('v2')
    article = Article.objects.get(url=url)
    text1 = article.get_version(v1)
    text2 = article.get_version(v2)
    title = article.metadata()['title']

    versions = article.versions()
    #index1 = [i for i, x in enumerate(versions) if x[1] == v1][0]
    #index2 = [i for i, x in enumerate(versions) if x[1] == v2][0]

    date1 = models.get_commit_date(v1).strftime(OUT_FORMAT)
    date2 = models.get_commit_date(v2).strftime(OUT_FORMAT)

    earlier1 = 1

    return render_to_response('diffview.html', {
            'title': title,
            'date1':date1, 'date2':date2,
            'text1':text1, 'text2':text2,
            'article_url': url, 'v1': v1, 'v2': v2,
            'form_action': 'upvote',
            })

def view(request):
    url = request.REQUEST.get('url')
    v = request.REQUEST.get('v')
    article = Article.objects.get(url=url)
    text = article.get_version(v)
    return HttpResponse(text, content_type='text/plain;charset=utf-8')

def article_view(request):
    url = request.REQUEST.get('url')
    article = Article.objects.get(url=url)
    metadata = article.metadata()
    versions = article.versions()


    rowinfo = []
    lastcommit = None
    for date, commit in versions:
        if lastcommit is None:
            diffl = ''
        else:
            diffl = '%s?%s' % (reverse(diffview),
                               urllib.urlencode(dict(url=url, v1=lastcommit, v2=commit)))

        link = '%s?%s' % (reverse(view),
                          urllib.urlencode(dict(url=url, v=commit)))
        rowinfo.append((link, diffl, date))
        lastcommit = commit
        rowinfo.reverse()

    return render_to_response('article_view.html', {'url':url,
                                             'metadata':metadata,
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

