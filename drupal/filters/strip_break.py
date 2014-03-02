__author__ = 'aleks'

from bs4 import Comment


def filter_strip_break(post, soup):
    comments = soup.find_all(text=lambda text: isinstance(text, Comment))

    for c in comments:
        if c.string == 'break':
            c.extract()
    return post, soup
