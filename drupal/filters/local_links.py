import re
import urllib
from urlparse import urlparse


def filter_local_links(rewriting, post, soup):
    """
    @type rewriting: map
    @type post: map
    @type soup: bs4.BeautifulSoup
    """
    matcher = re.compile('^[\s]*http://nevkontakte.(com|org.ru)', re.IGNORECASE)
    for t in soup.find_all('a'):
        if 'href' in t.attrs:
            if re.match(matcher, t['href']):
                t['href'] = re.sub(matcher, '', t['href'])

                href = urllib.unquote(t['href']).decode('utf-8')
                href = urlparse(href).path

                if href in rewriting:
                    t['href'] = rewriting[href]

    for t in soup.find_all('img'):
        if 'src' in t.attrs:
            t['src'] = re.sub(matcher, '', t['src'])

    return post, soup

