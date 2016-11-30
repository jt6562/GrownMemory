# encoding: utf-8

from db import *
import json
import peewee
import pytest

item_uuid = None


def setup_module(module):
    if not Photo.table_exists():
        Photo.create_table()

    utc = datetime.utcnow()
    n = Photo.create(
        name='test',
        itime=utc,
        ctime=utc,
        mtime=utc,
        state=PhotoProcessState.received)
    n.save()

    global item_uuid
    item_uuid = n.uuid


def test_create_item():
    # Check created item exist on setup_module
    with pytest.raises(peewee.DoesNotExist):
        r = Photo.get(Photo.uuid == "item_uuid")
    r = Photo.get(Photo.uuid == item_uuid)
    assert r.uuid == item_uuid


def test_get_all_item():
    r = Photo.select()
    for i in r:
        print json.dumps(model_to_dict(i), cls=ItemJSONEncoder, indent=4)


def test_get_item():
    r = Photo.select().where(Photo.uuid == item_uuid).first()  # same like get
    print json.dumps(model_to_dict(r), cls=ItemJSONEncoder, indent=4)
    print 11111, item_uuid
    assert r.uuid == item_uuid


def teardown_module(module):
    print item_uuid, 231
    r = Photo.get(Photo.uuid == item_uuid)
    r.delete_instance()
    r.save()
