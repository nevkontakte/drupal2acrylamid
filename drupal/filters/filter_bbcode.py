__author__ = 'aleks'

from bs4 import BeautifulSoup
import re


def filter_bbcode(post, soup):
    code = str(soup)

    code = code.replace('[b]', '<strong>')
    code = code.replace('[/b]', '</strong>')
    code = code.replace('[quote]', '<blockquote>')
    code = code.replace('[/quote]', '</blockquote>')

    code = re.sub(
        '\[url\](.*?)\[/url\]',
        '[\\1](\\1)',
        code
    )

    code = re.sub(
        '\[url=(.*?)\](.*?)\[/url\]',
        '[\\2](\\1)',
        code
    )

    soup = BeautifulSoup(code)

    return post, soup
