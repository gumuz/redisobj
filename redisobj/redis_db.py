from UserDict import DictMixin

import redis


# exception to be raise, when invalid data types are tried to be set
class InvalidDataType(Exception): pass


class RedisDB(DictMixin):
    """
    Dict interface to a redis database
    """
    def __init__(self, host='localhost', port=6379, db=0):
        """
        Setup connection to redis database
        """
        self.host = host
        self.port = port
        self.db = db

        self.redis = redis.StrictRedis(host=host, port=port, db=db)

    def __repr__(self):
        return "<RedisDB host:'%s' port:'%s' db:'%s' >" % (self.host, self.port, self.db)


    def __setitem__(self, key, value):
        """
        Emulate dict key set, like dict[key] = value
        """
        # keys can only be strings
        if not isinstance(key, str):
            raise InvalidDataType, "key needs to be of type str"

        # str and int can be set
        if isinstance(value, str) or isinstance(value, int):
            self.redis.set(key, value)

        # list can be set, only containing str or int
        elif isinstance(value, list) and all([isinstance(i, str) or isinstance(i, int) for i in value]):
            if key in self: del self[key]
            for i in value: self.redis.rpush(key, i)

        # sets can be set, only containing str or int
        elif isinstance(value, set) and all([isinstance(i, str) or isinstance(i, int) for i in value]):
            if key in self: del self[key]
            for i in value: self.redis.sadd(key, i)

        # dicts can be set, only containing str keys and str or int values
        elif isinstance(value, dict) and all([isinstance(i, str) or isinstance(i, int) for i in value.values()]) and all([isinstance(i, str) for i in value.keys()]):
            if key in self: del self[key]
            self.redis.hmset(key, value)

        # if none of the above, raise error
        else:
            raise InvalidDataType, "value needs to be of type str, \
                                    int, \
                                    a list containing str or int, \
                                    a set containing str or int or \
                                    a dict containing str or int"


    def __getitem__(self, key):
        """
        Emulate dict key get, like dict[key]
        """
        # keys can only be strings
        if not isinstance(key, str):
            raise InvalidDataType, "key needs to be of type str"

        # if key does not exist, raise KeyError
        if not self.redis.exists(key):
            raise KeyError

        value_type = self.redis.type(key)

        # use appropriate redis getter function, te retrieve values
        if value_type == 'string':
            value = self.redis.get(key)
        elif value_type == 'list':
            value = self.redis.lrange(key, 0, -1)
        elif value_type == 'set':
            value = self.redis.smembers(key)
        elif value_type == 'hash':
            value = self.redis.hgetall(key)

        return value

    def __delitem__(self, key):
        """
        Emulate dict key delete, like del dict[key]
        """
        # keys can only be strings
        if not isinstance(key, str):
            raise InvalidDataType, "key needs to be of type str"

        # perform getitem, to trigger KeyError if needed
        self.__getitem__(key) and self.redis.delete(key)


    def __contains__(self, key):
        """
        Emulate dict in-operator, like key in dict
        """
        return self.redis.exists(key)

    def keys(self):
        """
        Emulate dict keys() method to retrieve all keys from current db
        """
        return self.redis.keys()

    def clear(self):
        """
        Emulate dict clear() method to remove all keys from current db
        """
        self.redis.flushdb()
