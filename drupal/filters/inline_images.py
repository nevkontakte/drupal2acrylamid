__author__ = 'aleks'

from bs4 import NavigableString
import re


def filter_inline_images(post, soup):
    tags = soup.find_all(text=re.compile('\[inline:[^\]]+\.(jpg|png|gif)(?:=[^\]]+)?\]', re.IGNORECASE))

    for tag in tags:
        assert type(tag) == NavigableString
        tag.replace_with(soup.new_string(re.sub(
            '\[inline:([^\]]+\.(:?jpg|png|gif))(?:=([^\]]+))?\]',
            '[![\\1](/files/imagecache/Thumbinal/\\1)](/files/\\1)',
            tag.string,
            flags=re.IGNORECASE
        )))

    return post, soup
