#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lxml import etree
from os import path

import filecache

from acryl import Acrylamid
from drupal import Drupal
from drupal.filters import *
from functools import partial
import sys


@filecache.filecache(filecache.DAY)
def fetch_data(host, user, password, database, limit=None):
    dr = Drupal(host, user, password, database)
    return dr.fetch_posts(limit), dr.fetch_aliases(), dr.fetch_comments(limit)


def main():
    if not path.exists('conf.py'):
        print ("Error: importing must be run from Acrylamid root directory.")
        exit(1)

    ac = Acrylamid(
        'trnsl.1.1.20140106T112703Z.272ad6b61485e7b7.4bd3d9a1f4844b120bca07d047d4340b045cafdf',
        [filter_strip_break, filter_feature_image, filter_feature_video,
         filter_inline_images, filter_inline_attachments, filter_local_links, filter_bbcode, filter_markdownify]
    )

    host, user, password, db = sys.argv[1:5]
    posts, aliases, comments = fetch_data(host, user, password, db)

    for post in posts:
        ac.acquire_post(post)

    for comment in comments:
        if comment['name'] == 'Alek$':
            comment['mail'] = 'du-sky@ya.ru'
            comment['homepage'] = 'http://nevkontakte.com'
        ac.acquire_comment(comment)

    ac.acquire_aliases(aliases)

    local_rewrite_map = {}
    for (nid, aliases) in ac.aliases.items():
        post_path = '/' + ac.get_post_path(ac.posts[nid]) + '/'
        for a in aliases:
            a = '/' + a.lstrip('/')
            local_rewrite_map[a] = post_path

    ac.filters[ac.filters.index(filter_local_links)] = partial(filter_local_links, local_rewrite_map)

    # ac.save_posts()
    # ac.apache_redirects()
    ac.static_redirects()

    etree.ElementTree(
        ac.export_comments('http://nevkontakte.com/')
    ).write('comments.xml', pretty_print=True, encoding='utf-8')

if __name__ == "__main__":
    main()
