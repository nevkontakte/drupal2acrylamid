# -*- coding: utf-8 -*-
from MySQLdb import connect
from drupal.utils import gen_dict
from translate import Translator

__author__ = 'aleks'


class Drupal:
    def __init__(self, host, user, password, database):
        self.connection = connect(host, user, password, database)
        self.connection.query('SET NAMES `utf8`')

    def fetch_aliases(self):
        cur = self.connection.cursor()

        cur.execute("SELECT src, dst FROM drupal_url_alias WHERE src LIKE 'node/%' AND src NOT LIKE 'node/%/feed'")

        aliases = {}

        for alias in gen_dict(cur):
            nid = alias['src']
            nid = int(nid[len('node/'):])

            if nid not in aliases:
                aliases[nid] = []

            aliases[nid].append(alias['dst'].decode('utf8'))
        return aliases

    def fetch_posts(self, limit=None):
        cur = self.connection.cursor()

        sql = """SELECT node.nid,
                        node.title,
                        node_revisions.body,
                        node.created,
                        node.status,
                        node.type
                    FROM (drupal_node node
                        JOIN drupal_node_revisions node_revisions ON node.vid = node_revisions.vid)
                    WHERE (node.type = 'blog' OR node.type = 'page')
                    ORDER BY nid DESC"""
        if limit is not None:
            sql += " LIMIT " + str(limit)

        cur.execute(sql)

        return list(gen_dict(cur))

    def fetch_comments(self, limit=None):
        cur = self.connection.cursor()
        sql = """SELECT cid, pid, nid, comment, hostname, timestamp, name, mail, homepage
            FROM drupal_comments
            WHERE status = 0"""
        if limit is not None:
            sql += " LIMIT " + str(limit)
        cur.execute(sql)
        return list(gen_dict(cur))