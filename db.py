# encoding: utf-8

from peewee import *
from datetime import datetime
import enum  # enum34
from playhouse.shortcuts import (RetryOperationalError, model_to_dict,
                                 dict_to_model)
from uuid import uuid4
import json


def get_db_config():
    from os import path
    from configobj import ConfigObj
    conf_path = path.join(path.dirname(path.abspath(__file__)), 'config.ini')
    conf = ConfigObj(conf_path)
    return conf['db']


db_config = get_db_config()


class MySQLDatabaseRetry(RetryOperationalError, MySQLDatabase):
    pass


database = MySQLDatabaseRetry(
    db_config.get('database', 'photo_collector'),
    user=db_config['user'],
    passwd=db_config['password'],
    host=db_config.get('host', 'localhost'),
    port=int(db_config.get('port', 3306)))


class PhotoProcessState(enum.Enum):
    received = 1
    parsing = 2
    parsed = 3
    outputting = 4
    outputted = 5


class EnumField(FixedCharField):

    def __init__(self, enum_value, *args, **kwargs):
        super(EnumField, self).__init__(*args, **kwargs)
        self.enum_value = enum_value

    def db_value(self, value):
        if isinstance(value, enum.Enum):
            return value.name
        return super(EnumField, self).db_value(value)

    def python_value(self, value):
        return self.enum_value[value]


class LongBlobField(BlobField):
    db_field = 'longblob'


class MySQLModel(Model):

    class Meta:
        database = database


class Photo(MySQLModel):
    uuid = CharField(
        max_length=32, unique=True, index=True, default=uuid4().hex)
    name = CharField(null=True)
    itime = DateTimeField(default=datetime.utcnow())
    ctime = DateTimeField(null=True)
    description = TextField(null=True)
    state = EnumField(PhotoProcessState, default=PhotoProcessState.received)

    file_type = CharField(default='image')
    file_orgin_name = CharField(default='null')
    file_ext = CharField(default='jpg')
    hash = CharField(unique=True)
    img_eigen = CharField(null=True)

    width = IntegerField(null=True)
    height = IntegerField(null=True)

    orientation = IntegerField(null=True)
    make = CharField(null=True)
    model = CharField(null=True)
    location = CharField(null=True)

    class Meta:
        db_table = 'photos'


class ConflictPhoto(MySQLModel):
    # TODO, implement this

    exist_photo = ForeignKeyField(Photo, related_name='conflict_photos')

    class Meta:
        db_table = 'conflict_photos'


try:
    database.create_tables([Photo, ConflictPhoto])
except InternalError:
    pass


class ItemJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, enum.Enum):
            return obj.name
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


if __name__ == '__main__':
    if not Photo.table_exists():
        Photo.create_table()
    utc = datetime.utcnow()
    n = Photo.create(
        name='test', ctime=utc, mtime=utc, state=PhotoProcessState.received)
    n.save()

    r = Photo.select()
    import json
    for i in r:
        print json.dumps(model_to_dict(i), cls=ItemJSONEncoder, indent=4)

    n.delete_instance()
    n.save()
