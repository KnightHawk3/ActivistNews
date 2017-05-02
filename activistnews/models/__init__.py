# -*- coding: utf-8 -*-
from mongoengine import Document, connect, StringField, DateTimeField, \
                        ListField, EmbeddedDocumentField, EmbeddedDocument
from datetime import datetime

DB_NAME = "activistnews"

class Item(EmbeddedDocument):
    title = StringField(required=True)
    link = StringField(required=True)
    description = StringField(required=True)
    pubdate = DateTimeField(required=True, default=datetime.now)
    creator = StringField(required=False)

class RSSFeed(Document):
    url = StringField(required=True)
    name = StringField(required=True)
    description = StringField(required=False)
    date = DateTimeField(required=True, default=datetime.now)
    items = ListField(EmbeddedDocumentField(Item))

connect(DB_NAME)
