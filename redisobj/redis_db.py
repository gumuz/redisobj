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
        elif isinstance(value, list):
            if not all([isinstance(i, str) or isinstance(i, int) for i in value]):
                raise InvalidDataType, "lists can only contain values of type str or int"

            if key in self: del self[key]
            for i in value: self.redis.rpush(key, i)

        # sets can be set, only containing str or int
        elif isinstance(value, set):
            if not all([isinstance(i, str) or isinstance(i, int) for i in value]):
                raise InvalidDataType, "sets can only contain values of type str or int"

            if key in self: del self[key]
            for i in value: self.redis.sadd(key, i)

        # dicts can be set, only containing str keys and str or int values
        elif isinstance(value, dict):
            if not all([isinstance(i, str) or isinstance(i, int) for i in value.values()]) or not all([isinstance(i, str) for i in value.keys()]):
                raise InvalidDataType, "dicts can only contain keys of type str and values of type str or int"

            if key in self: del self[key]
            self.redis.hmset(key, value)
        # if none of the above, raise error
        else:
            raise InvalidDataType, "value needs to be of type str, int, set, list or dict"


    def __getitem__(self, key):
        """
        Emulate dict key get, like dict[key]
        """
        # keys can only be strings
        if not isinstance(key, str):
            raise InvalidDataType, "key needs to be of type str"

        # if key does not exist, raise KeyError
        if not self.redis.exists(key):
            raise KeyError, "Key '%s' does not exist" % key

        value_type = self.redis.type(key)

        # use appropriate redis getter function, te retrieve values
        if value_type == 'string':
            return self.redis.get(key)
        elif value_type == 'list':
            return self.redis.lrange(key, 0, -1)
        elif value_type == 'set':
            return self.redis.smembers(key)
        elif value_type == 'hash':
            return self.redis.hgetall(key)


    def __delitem__(self, key):
        """
        Emulate dict key delete, like del dict[key]
        """
        # keys can only be strings
        if not isinstance(key, str):
            raise InvalidDataType, "key needs to be of type str"

        # perform getitem, to trigger KeyError if needed
        return self.__getitem__(key) and self.redis.delete(key)


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
