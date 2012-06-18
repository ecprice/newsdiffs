from django.shortcuts import render_to_response, get_object_or_404
from models import Article
from django.http import HttpResponse, HttpResponseRedirect
import re

def index(request):
    articles = []
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
                diffl = 'diffview?url=%s&v1=%s&v2=%s' % (url, lastcommit, commit)
            link = 'view?url=%s&v=%s' % (url, commit)
            rowinfo.append((link, diffl, date))
            lastcommit = commit

        rowinfo.reverse()
        print url, vs, rowinfo
        articles.append((url, nc, rowinfo))
    articles.sort(key = lambda x: (x[1], x[2][0][2]), reverse=True)
    return render_to_response('index.html', {'articles': articles})


def diffview(request):
    url = request.REQUEST.get('url')
    v1 = request.REQUEST.get('v1')
    v2 = request.REQUEST.get('v2')
    #article = Article.objects.get(url=url)
    #text1 = article.get_version(v1)
    #text2 = article.get_version(v2)
    url_template = 'view?url='+url+'&v=%s'

    return render_to_response('diffview.html', {'url': url,
                                                'url1':url_template % v1,
                                                'url2':url_template % v2})

def view(request):
    url = request.REQUEST.get('url')
    v = request.REQUEST.get('v')
    article = Article.objects.get(url=url)
    text = article.get_version(v)
    return HttpResponse(text, content_type='text/plain;charset=utf-8')
