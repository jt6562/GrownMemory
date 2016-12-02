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
    conf_path = path.join(path.dirname(path.abspath(__file__)), '..','config.ini')
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



class ItemJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, enum.Enum):
            return obj.name
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

