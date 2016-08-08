# -*- coding: utf-8 -*-

from peewee import *
from src.conf import SAVER_FILE
from threading import Lock

db = SqliteDatabase(SAVER_FILE)
DB_LOCK = Lock()


class Saver(Model):
    sn = CharField(index=True, unique=True)
    img_url = CharField(index=True)
    filepath = CharField()
    status = BooleanField(index=True, default=False)

    class Meta:
        database = db


def init_db():
    db.connect()
    try:
        db.create_tables([Saver, ])
    except OperationalError:
        pass
