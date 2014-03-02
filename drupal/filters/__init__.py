from bs4 import BeautifulSoup
from drupal.filters.feature_image import filter_feature_image
from drupal.filters.feature_video import filter_feature_video
from drupal.filters.markdown import filter_markdownify
from drupal.filters.inline_images import filter_inline_images
from drupal.filters.strip_break import filter_strip_break
from drupal.filters.filter_bbcode import filter_bbcode
from drupal.filters.inline_attachments import filter_inline_attachments
from drupal.filters.local_links import filter_local_links


def apply_filters(post, flts):
    soup = BeautifulSoup(post['body'], "lxml")
    del post['body']

    for flt in flts:
        post, soup = flt(post, soup)

    post['body'] = u''.join(list(unicode(c) for c in soup.body.children)).strip()
    return post