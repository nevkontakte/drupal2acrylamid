__author__ = 'aleks'
# -*- coding: utf-8 -*-

import re
from bs4 import Tag


def _feature_video_title(tag):
    previous = tag.previous_element
    while (previous is not None) and (type(previous) != Tag or previous.name == 'p'):
        previous = previous.previous_element

    if previous.name != 'h3':
        raise LookupError()

    title = re.sub('^P\.?(\s+)?S\.?\s+', '', previous.string, 1)
    title = title.replace(u' - ', u' — ')
    return previous, title


def filter_feature_video(post, soup):
    tags = soup.find_all('iframe', src=re.compile('youtube.com')) + soup.find_all('object')

    for tag in reversed(tags):

        try:
            previous, title = _feature_video_title(tag)
        except LookupError:
            continue

        if tag.name == 'iframe':
            match = re.search('/([^/]+)$', tag['src'])
        else:
            match = re.search('/([^/?&]+)[?&]', tag.embed['src'])

        if match:
            post['feature_video'] = {
                'id': match.group(1),
                'title': title
            }

        tag.decompose()
        previous.decompose()
        break

    return post, soup
