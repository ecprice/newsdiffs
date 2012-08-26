GIT_PROGRAM = 'git'

def mkdir_p(path):
    import os, errno
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise

def canonicalize_url(url):
    return url.split('?')[0].split('#')[0].strip()

def strip_prefix(string, prefix):
    if string.startswith(prefix):
        string = string[len(prefix):]
    return string

def url_to_filename(url):
    return strip_prefix(url, 'http://').rstrip('/')

def grab_url(url, max_depth=5, opener=None):
    import cookielib, urllib2, socket, time
    if opener is None:
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    retry = False
    try:
        text = opener.open(url, timeout=5).read()
        if '<title>NY Times Advertisement</title>' in text:
            retry = True
    except socket.timeout:
        retry = True
    if retry:
        if max_depth == 0:
            raise Exception('Too many attempts to download %s' % url)
        time.sleep(0.5)
        return grab_url(url, max_depth-1, opener)
    return text

def strip_whitespace(text):
    lines = text.split('\n')
    return '\n'.join(x.strip().rstrip(u'\xa0') for x in lines).strip() + '\n'
