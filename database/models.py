# encoding: utf-8

from peewee import *
from datetime import datetime
import enum  # enum34
from uuid import uuid4
import json
from db import database


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
    itime = DateTimeField(default=datetime.utcnow())
    ctime = DateTimeField(null=True)
    description = TextField(null=True)
    state = EnumField(PhotoProcessState, default=PhotoProcessState.received)

    file_type = CharField(default='image')
    file_orgin_name = CharField(null=True)
    file_ext = CharField(default='jpg')
    file_hash = CharField(unique=True)
    img_hash = CharField(null=True)

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
    database.create_tables([Photo])
except InternalError:
    pass
