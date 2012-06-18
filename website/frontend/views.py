from django.shortcuts import render_to_response, get_object_or_404
from models import Article
import models
from django.http import HttpResponse, HttpResponseRedirect
import re


OUT_FORMAT = '%B %d, %Y at %l:%M%P EDT'

def browse(request):
    articles = []
    models._reset_metadata()
    for article in Article.objects.all():
        url = article.url
        if 'blogs.nytimes.com' in url: #XXX temporary
            continue
        vs = article.versions()
        nc = len(vs)
        if nc < 1:
            continue
        rowinfo = []
        vs.reverse()
        lastcommit = None
        for date, commit in vs:
            if lastcommit is None:
                diffl = ''
            else:
                diffl = '../diffview?url=%s&v1=%s&v2=%s' % (url, lastcommit, commit)
            link = '../view?url=%s&v=%s' % (url, commit)
            rowinfo.append((link, diffl, date.strftime(OUT_FORMAT)))
            lastcommit = commit
        rowinfo.reverse()
        (date, title, byline) = article.metadata()
        articles.append((url, date, title, byline, nc, rowinfo))
    articles.sort(key = lambda x: (x[-2] > 1, x[-1][0][2]), reverse=True)
    return render_to_response('index.html', {'articles': articles})


def diffview(request):
    url = request.REQUEST.get('url')
    v1 = request.REQUEST.get('v1')
    v2 = request.REQUEST.get('v2')
    article = Article.objects.get(url=url)
    #text1 = article.get_version(v1)
    #text2 = article.get_version(v2)
    url_template = 'view?url='+url+'&v=%s'
    title = article.metadata()[1]
    date1 = models.get_commit_date(v1).strftime(OUT_FORMAT)
    date2 = models.get_commit_date(v2).strftime(OUT_FORMAT)
    return render_to_response('diffview_templated.html', {'title': title,
                                                          'date1':date1,
                                                          'date2':date2,
                                                'url1':url_template % v1,
                                                'url2':url_template % v2})

def view(request):
    url = request.REQUEST.get('url')
    v = request.REQUEST.get('v')
    article = Article.objects.get(url=url)
    text = article.get_version(v)
    return HttpResponse(text, content_type='text/plain;charset=utf-8')

def about(request):
    return render_to_response('about.html', {})

def examples(request):
    return render_to_response('examples.html', {})

def contact(request):
    return render_to_response('contact.html', {})

def front(request):
    return render_to_response('front.html', {})
