__author__ = 'aleks'

from bs4 import NavigableString
import re


def filter_inline_attachments(post, soup):
    tags = soup.find_all(text=re.compile('\[file:(.+?)=([^\]]+?)\]'))

    for tag in tags:
        assert type(tag) == NavigableString
        tag.replace_with(soup.new_string(re.sub(
            '\[file:(.*?)=([^\]]+)?\]',
            '[\\2](/files/\\1)',
            tag.string,
            flags=re.IGNORECASE
        )))
    tags = soup.find_all(text=re.compile('\[inline:(.+?)\]'))

    for tag in tags:
        assert type(tag) == NavigableString
        tag.replace_with(soup.new_string(re.sub(
            '\[inline:(.+?)\]',
            '[\\1](/files/\\1)',
            tag.string,
            flags=re.IGNORECASE
        )))

    return post, soup
