import re

from baseparser import BaseParser
from bs4 import BeautifulSoup


paragraph_wrapper_re = re.compile(r'.*\bStoryBodyCompanionColumn\b.*')

class NYTParser(BaseParser):
    SUFFIX = '?pagewanted=all'
    domains = ['www.nytimes.com']

    feeder_pat   = '^https?://www.nytimes.com/201'
    feeder_pages = ['http://www.nytimes.com/',
                    'http://www.nytimes.com/pages/world/',
                    'http://www.nytimes.com/pages/national/',
                    'http://www.nytimes.com/pages/politics/',
                    'http://www.nytimes.com/pages/nyregion/',
                    'http://www.nytimes.com/pages/business/',
                    'http://www.nytimes.com/pages/technology/',
                    'http://www.nytimes.com/pages/sports/',
                    'http://dealbook.nytimes.com/',
                    'http://www.nytimes.com/pages/science/',
                    'http://www.nytimes.com/pages/health/',
                    'http://www.nytimes.com/pages/arts/',
                    'http://www.nytimes.com/pages/style/',
                    'http://www.nytimes.com/pages/opinion/',
                    'http://www.nytimes.com/pages/automobiles/',
                    'http://www.nytimes.com/pages/books/',
                    'http://www.nytimes.com/crosswords/',
                    'http://www.nytimes.com/pages/dining/',
                    'http://www.nytimes.com/pages/education/',
                    'http://www.nytimes.com/pages/fashion/',
                    'http://www.nytimes.com/pages/garden/',
                    'http://www.nytimes.com/pages/magazine/',
                    'http://www.nytimes.com/pages/business/media/',
                    'http://www.nytimes.com/pages/movies/',
                    'http://www.nytimes.com/pages/arts/music/',
                    'http://www.nytimes.com/pages/obituaries/',
                    'http://www.nytimes.com/pages/realestate/',
                    'http://www.nytimes.com/pages/t-magazine/',
                    'http://www.nytimes.com/pages/arts/television/',
                    'http://www.nytimes.com/pages/theater/',
                    'http://www.nytimes.com/pages/travel/',
                    'http://www.nytimes.com/pages/fashion/weddings/',
                    'http://www.nytimes.com/pages/todayspaper/',
                    'http://topics.nytimes.com/top/opinion/thepubliceditor/']

    def _parse(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        self.meta = soup.findAll('meta')

        seo_title = soup.find('meta', attrs={'name': 'hdl'})
        if seo_title:
            seo_title = seo_title.get('content')
        else:
            seo_title = soup.find('meta', attrs={'property':"og:title"}).get('content')

        tmp = soup.find('meta', attrs={'name': 'hdl_p'})
        if tmp and tmp.get('content'):
            self.title = tmp.get('content')
        else:
            meta_og_title = soup.find('meta', attrs={'property': 'og:title'})
            if meta_og_title:
                self.title = meta_og_title.get('content')
        if not self.title:
            self.title = seo_title

        try:
            self.date = soup.find('meta', attrs={'name':'dat'}).get('content')
            self.byline = soup.find('meta', attrs={'name':'byl'}).get('content')
        except AttributeError:
            try:
                self.date = soup.find('time').getText()
                self.byline = soup.find('p', attrs={'itemprop': 'author creator'}).getText()
            except:
                self.real_article = False
                return
        p_tags = sum([list(soup.findAll('p', attrs=restriction))
                      for restriction in [{'itemprop': 'articleBody'},
                                          {'itemprop': 'reviewBody'},
                                          {'class': 'story-body-text story-content'}
                                      ]],
                     [])

        if not p_tags:
            p_tags = sum([div.findAll(['p', 'h2']) for div in soup.findAll('div', attrs={'class': paragraph_wrapper_re})], [])
        if not p_tags:
            article = soup.find('article', attrs={'id': 'story'})
            article_p_tags = article.findAll('p')

            header_p_tags = article.find('header').findAll('p')
            bottom_of_article = article.find('div', attrs={'class': 'bottom-of-article'})

            p_tags = [
                p_tag for p_tag in article_p_tags
                if (
                    p_tag.getText() and
                    # Remove header p_tags because it duplicates the title
                    p_tag not in header_p_tags and
                    # Remove bottom of article p_tags because we add them as the correction
                    bottom_of_article not in p_tag.parents and
                    p_tag.getText() != 'Advertisement'
                )
            ]

        div = soup.find('div', attrs={'class': 'story-addendum story-content theme-correction'})
        if div:
            p_tags += [div]
        footer = soup.find('footer', attrs={'class': 'story-footer story-content'})
        
        if footer:
            p_tags += list(footer.findAll(lambda x: x.get('class') is not None and 'story-print-citation' not in x.get('class') and x.name == 'p'))

        main_body = '\n\n'.join([p.getText() for p in p_tags])
        authorids = soup.find('div', attrs={'class':'authorIdentification'})
        authorid = authorids.getText() if authorids else ''

        top_correction = '\n'.join(x.getText() for x in
                                   soup.findAll('nyt_correction_top')) or '\n'

        bottom_correction = ''
        correction_bottom_tags = soup.findAll('nyt_correction_bottom')
        if correction_bottom_tags:
            bottom_correction = '\n'.join(x.getText() for x in correction_bottom_tags)
        if not correction_bottom_tags:
            bottom_of_article = soup.find('div', attrs={'class': 'bottom-of-article'})
            if bottom_of_article:
                bottom_correction = bottom_of_article.getText()
                print_info_index = bottom_correction.find('A version of this article appears in print on')
                if print_info_index > -1:
                    bottom_correction = bottom_correction[:print_info_index]
        if not bottom_correction:
            bottom_correction = '\n'

        self.body = '\n'.join([
            top_correction,
            main_body,
            authorid,
            bottom_correction,
        ])
