import uuid
import redis

import settings

class ObjectNotInitializedError(Exception):
    pass

class ObjectNotFoundError(Exception):
    pass

try:
    import cPickle as pickle
except:
    import pickle


pool = redis.ConnectionPool(**settings.REDIS_CONNECTION)

class ConnectionPooler(object):
    '''Just the mother object'''

    def __init__(self):
        self.client = redis.Redis(connection_pool=pool)

class RedisManager(ConnectionPooler):
    '''A Django's ORM style object manager for redis'''

    def __init__(self, model):
        super(RedisManager, self).__init__()
        self.model = model

    def filter(self, **kwargs):
        '''Filtering implementation'''
        raise NotImplementedError

    def get(self, key):
        '''Returns a single object by key'''
        value = self.client.get(key)
        if value:
            return self.model(key=key, value=value)
            #return self.model(**{'key': key, 'value':value})
        else:
            raise ObjectNotFoundError()

class ModelBase(type):
    '''Redis model metaclass'''

    def __new__(cls, name, bases, attrs):
        new_class = type(name, bases, attrs)
        setattr(new_class, 'objects', RedisManager(cls))
        return new_class

    def __init__(cls, name, bases, attr):
        super(ModelBase, cls).__init__(name, bases, attr)

class RedisModel(ConnectionPooler):
    '''A class that wraps a python object to redis'''

    __metaclass__ = ModelBase

    def __init__(self, key='', value=''):
        super(RedisModel, self).__init__()
        self.key = key
        _value = value
        try:
            self.value = pickle.loads(_value)
        except Exception:
            self.value = _value

    def delete(self):
        '''Deletes object'''
        if self.key:
            return self.client.delete(self.key)
        else:
            error_msg = 'The object: %s was not fetched from Redis' % \
                    self.__unicode__()
            raise ObjectNotInitializedError(error_msg)

    def save(self, timeout=0):
        '''Accepts key expiration'''
        if not self.key:
            self.key = uuid.uuid4().hex

        if timeout == 0:
            result = self.client.set(self.key, pickle.dumps(self.value))
        elif timeout > 0:
            result = self.client.setex(self.key,
                    pickle.dumps(self.value), int(timeout))
        else:
            raise Exception("timeout can not be negative")
        return self if result else None

    def persists(self):
        '''Calls the PERSISTS redis command for the key'''
        raise NotImplementedError

    def __unicode__(self):
        return unicode(self)

class ImageLink(RedisModel):
    pass
