import re
from bs4 import NavigableString

__author__ = 'aleks'


def _is_feature_image(tag):
    if not tag.name == 'img':
        return False

    return ('align' in tag.attrs and tag['align'] == 'right') or \
           ('style' in tag.attrs and re.match('float:\\s*right', tag['style'], re.I))


def filter_feature_image(post, soup):
    img = soup.find(_is_feature_image)
    if img is not None:
        post['feature'] = img['src']
        img.extract()
    else:
        tags = soup.find_all(text=re.compile('\[inline:[^\]]+\.(jpg|png|gif)\]'))

        for tag in tags:
            assert type(tag) == NavigableString

            parent = tag.parent
            if parent.name == 'div' and 'style' in parent.attrs and re.match('float:\\s*right', parent['style'], re.I):
                match = re.search('\[inline:([^\]]+\.(:?jpg|png|gif))\]', tag.string)
                post['feature'] = 'http://nevkontakte.com/files/imagecache/Thumbinal/' + match.group(1)
                parent.extract()

    if 'feature' in post:
        post['feature'] = re.sub('^[\s]*http://nevkontakte.(com|org.ru)', '', post['feature'])

    return post, soup
