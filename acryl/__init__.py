# -*- coding: utf-8 -*-
from drupal.filters import apply_filters
from os.path import join, dirname, exists
from os import makedirs

__author__ = 'aleks'

from drupal.translate import Translator
from datetime import datetime
import re
import string
import unidecode
from os import path, mkdir
import yaml
from lxml.etree import Element, SubElement, CDATA


class Acrylamid:
    posts = {}
    aliases = {}
    filters = []
    comments = {}
    nsmap = {
        'content': 'http://purl.org/rss/1.0/modules/content/',
        'dsq': 'http://www.disqus.com/',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'wp': 'http://wordpress.org/export/1.0/',
    }

    def __init__(self, api_key, filters):
        """
        @type filters: list
        """
        self.t = Translator(api_key)
        self.expression = '[' + re.escape(string.punctuation) + string.whitespace + ']+'
        self.filters = filters

    def acquire_post(self, entry):
        slug = re.sub('(\'е|\'а|\'у|\'ю|\'е)(\s|$)', '\\2', entry['title'])
        slug = self.t.translate(slug)
        slug = re.sub(self.expression, '-', slug).strip('-')
        slug = unidecode.unidecode(slug)

        post = {
            'title': entry['title'].decode('utf8'),
            'type': 'entry' if entry['type'] == 'blog' else 'page',
            'date': datetime.fromtimestamp(entry['created']),
            'filters': [],
            'draft': entry['status'] == 0,
            'body': entry['body'].decode('utf8'),
            'drupal_nid': entry['nid'],
            'slug': slug,
        }
        # print post['title'], post['drupal_nid'], slug.encode('utf8')

        self.posts[entry['nid']] = post

    def acquire_aliases(self, aliases):
        for nid in aliases:
            if nid not in self.aliases:
                self.aliases[nid] = []

            self.aliases[nid] += aliases[nid]

    def save_posts(self, content_dir='./content'):
        for nid in self.posts:
            self.save_post(apply_filters(self.posts[nid], self.filters), content_dir)

    def save_post(self, post, content_dir):
        body = post['body']
        del post['body']

        post_path = path.join(content_dir, self.get_post_path(post) + ".txt")
        parent_dir = path.dirname(post_path)

        if not path.isdir(parent_dir):
            mkdir(parent_dir)

        stream = open(post_path, 'w')

        stream.write("---\n")

        yaml.dump(post, stream,
                  default_flow_style=None,
                  Dumper=yaml.SafeDumper,
                  encoding='UTF-8',
                  allow_unicode=True,
                  )

        stream.write("---\n")
        stream.write(body.encode('utf-8'))
        stream.close()

        post['body'] = body

    @staticmethod
    def get_post_path(post):
        slug = post['slug']

        if post['type'] == 'page':
            return "pages/%s" % slug
        else:
            return "%d/%s" % (post['date'].year, slug)

    def apache_redirects(self, assets_dir='./assets'):
        stream = open(path.join(assets_dir, '.htaccess'), 'w')

        with stream:
            stream.write("RewriteEngine on\n")

            for nid in self.aliases:
                for src in self.aliases[nid]:
                    if nid not in self.posts.keys():
                        continue

                    dst = self.get_post_path(self.posts[nid])
                    line = "RewriteRule ^%s$ %s [L,R=301]\n" % (re.escape(src), dst)
                    stream.write(line.encode('utf8'))

    def acquire_comment(self, entry):
        nid = entry['nid']

        for p in entry:
            if isinstance(entry[p], str):
                entry[p] = entry[p].decode('utf8')

        comment = {
            'id': entry['cid'],
            'author': entry['name'],
            'author_email': entry['mail'],
            'author_IP': entry['hostname'],
            'date_gmt': datetime.fromtimestamp(entry['timestamp']),
            'content': entry['comment'],
            'approved': 1,
        }

        if entry['pid'] != 0:
            comment['parent'] = entry['pid']

        if entry['homepage'] != '':
            comment['author_url'] = entry['homepage']

        if nid not in self.comments:
            self.comments[nid] = []

        self.comments[nid].append(comment)

    def export_comment(self, comment):
        wp = self.nsmap['wp']

        comment_node = Element('{%s}comment' % wp, nsmap=self.nsmap)

        for prop in comment:
            p = SubElement(comment_node, '{%s}comment_%s' % (wp, prop))
            # print property, comment[property].decode('utf-8')

            if isinstance(comment[prop], datetime) or \
                    isinstance(comment[prop], int) or \
                    isinstance(comment[prop], long):
                p.text = str(comment[prop])
            else:
                p.text = comment[prop]

        return comment_node

    def export_post_comments(self, nid, base_url):
        wp = self.nsmap['wp']
        content = self.nsmap['content']
        dsq = self.nsmap['dsq']

        post = self.posts[nid]

        item_node = Element('item', nsmap=self.nsmap)
        SubElement(item_node, 'title').text = post['title']
        SubElement(item_node, 'link').text = base_url + self.get_post_path(post) + '/'
        SubElement(item_node, '{%s}encoded' % content).text = CDATA(post['body'])
        SubElement(item_node, '{%s}thread_identifier' % dsq).text = '/' + self.get_post_path(post) + '/'
        SubElement(item_node, '{%s}post_date_gmt' % wp).text = str(post['date'])
        SubElement(item_node, '{%s}comment_status' % wp).text = 'open'

        if nid in self.comments.keys():
            for comment in self.comments[nid]:
                item_node.append(self.export_comment(comment))

        return item_node

    def export_comments(self, base_url):
        rss = Element('rss', self.nsmap)
        channel = SubElement(rss, 'channel')

        for nid in self.comments:
            channel.append(self.export_post_comments(nid, base_url))

        return rss

    def static_redirects(self, assets_dir='./assets'):
        for nid in self.aliases:
            for src in self.aliases[nid]:
                if nid not in self.posts.keys():
                    continue

                dst = self.get_post_path(self.posts[nid])
                stub_path = join(assets_dir, src, 'index.html')
                dir_name = dirname(stub_path)
                exists(dir_name) or makedirs(dir_name)
                stream = open(stub_path, 'w')
                with stream:
                    stream.write(self.redirect_template(dst).encode('utf8'))

    @staticmethod
    def redirect_template(target):
        return """
            <!DOCTYPE html>
            <html>
            <head>
            <link rel="canonical" href="{0}"/>
            <meta http-equiv="content-type" content="text/html; charset=utf-8" />
            <meta http-equiv="refresh" content="0;url={0}" />
            </head>
            </html>
            """.format("/" + target)