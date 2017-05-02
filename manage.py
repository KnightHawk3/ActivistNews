#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import sys
import click
from bottle import static_file, Bottle, run, TEMPLATE_PATH
from beaker.middleware import SessionMiddleware

from activistnews import settings
from activistnews.routes import Routes


TEMPLATE_PATH.insert(0, settings.TEMPLATE_PATH)
session_opts = {
    'session.type': 'file',
    'session.auto': True
}

app = SessionMiddleware(Bottle(), session_opts)

# Bottle Routes
app.wrap_app.merge(Routes)


@app.wrap_app.route('/assets/<path:path>', name='assets')
def assets(path):
    yield static_file(path, root=settings.STATIC_PATH)


@click.group()
def cmds():
    pass


@cmds.command()
@click.option('--port', default=os.environ.get('PORT', 8080), type=int,
              help=u'Set application server port!')
@click.option('--ip', default='0.0.0.0', type=str,
              help=u'Set application server ip!')
@click.option('--debug', default=False,
              help=u'Set application server debug!')
def runserver(port, ip, debug):
    click.echo('Start server at: {}:{}'.format(ip, port))
    run(app=app, host=ip, port=port, debug=debug, reloader=debug)


@cmds.command()
@click.option('--database-host', default='mongodb://localhost/', type=str,
              help=u'The host of the database')
@click.option('--database-name', default='activistnews', type=str,
              help=u'The name of the database')
def fetch(database_host, database_name):
    import feedparser
    from time import mktime
    from datetime import datetime
    from mongoengine import connect
    from activistnews.models import RSSFeed, Item

    # Connect to the database
    uri = database_host + database_name
    connect(database_name, host=uri)

    # Fetch the items
    # TODO: Async this
    for feed in RSSFeed.objects:
        d = feedparser.parse(feed.url)
        import pprint
        items = []
        for link in d['entries']:
            item = Item(title=link['title'],
                        description=link['summary'],
                        pubdate=datetime.fromtimestamp(
                            mktime(link['published_parsed'])),
                        creator=link['author'],
                        link=link['link'])
            items.append(item)
        feed.items = items
        feed.save()

@cmds.command()
@click.option('--feed', type=str, help=u'The feed to add')
@click.option('--database-host', default='mongodb://localhost/', type=str,
              help=u'The host of the database')
@click.option('--database-name', default='activistnews', type=str,
              help=u'The name of the database')
def add(feed, database_host, database_name):
    import feedparser
    from mongoengine import connect
    from activistnews.models import RSSFeed

    # Connect to the database
    uri = database_host + database_name
    connect(database_name, host=uri)

    # Basic check for a duplicate
    duplicate = False
    for feed in RSSFeed.objects:
        if feed.url == feed:
            duplicate = True
    if duplicate:
        return

    # Get the feed and add it to the database
    d = feedparser.parse(feed)
    rssfeed = RSSFeed(name=d['feed']['title'],
                      url=feed,
                      description=d['feed']['subtitle'])
    rssfeed.save()


@cmds.command()
def test():
    import unittest
    loader = unittest.TestLoader()
    tests = loader.discover('tests')
    testRunner = unittest.runner.TextTestRunner()
    r = testRunner.run(tests)
    if r.wasSuccessful() == False:
        sys.exit(1)
    return 0


if __name__ == "__main__":
    cmds()
