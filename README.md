Redis Object
============

A Python dictionary-like interface to a [Redis](http://redis.io/) database, implementing all methods provided by the
[UserDict](http://docs.python.org/library/userdict.html) mixin.

**caution**: This is to be used in a interactive shell environment, not in production as a library to interface
with your Redis database.

Dependencies
------------

* [redis-py](https://github.com/andymccurdy/redis-py)
* [mock](http://code.google.com/p/mock/) to run the unit tests

Usage
-----

### Connecting to a Redis database

    >>> import redisobj
    >>> rdb = redisobj.RedisDB(host='localhost', port=6379, db=0)

### Dictionary operations

A RedisDB object can be used like an ordinary Python dictionary object.

#### Getting and setting

    >>> rdb["key"] = "value"
    >>> rdb["key"]
    'value'

#### IN-operator

    >>> "key" in rdb
    True

#### Delete key

    >>> del rdb["key"]
    >>> "key" in rdb
    False

#### Keys

    >>> rdb.keys()
    ['key1', 'key2', 'key3']

### Clear

Be careful, this deletes all keys from the current database.

    >>> rdb.clear()
    >>> rdb.keys()
    []

### Exceptions

#### KeyError

Just like a normal dictionary, a KeyError will be raised when accessing a non-existing key.

    >>> rdb["non-existing-key"]
    KeyError: key 'non-existing-key' does not exist

#### InvalidDataType Exception

The only accepted values are string, integer, list, set or dictionary.

    >>> rdb["key"] = 1.5
    InvalidDataType: value needs to be of type str, int, set, list or dict

The list, set and dict types can only contain string or integer values.

    >>> rdb["key"] = [1,2,3,{"a":"b"}]
    InvalidDataType: lists can only contain values of type str or int

### Data types

#### Strings

    >>> rdb["my_string"] = "this is my string"
    >>> rdb["my_string"]
    'this is my string'

#### Integers

Integers can be set, but will always be returned as strings.

    >>> rdb["my_integer"] = 1
    >>> rdb["my_integer"]
    '1'

#### Lists

Lists can contain integers, but integer values will always be returned as strings.

    >>> rdb["my_list"] = [1,2,'this is a string']
    >>> rdb["my_list"]
    ['1','2','this is a string']

#### Sets

Sets can contain integers, but integer values will always be returned as strings.

    >>> rdb["my_set"] = set([1,2,'this is a string'])
    >>> rdb["my_set"]
    set(['1','2','this is a string'])

#### Hashes (dictionaries)

Hashes (dictionaries) can contain integers, but integer values will always be returned as strings. Keys should
always be strings.

    >>> rdb["my_hash"] = {"a":2,"b":"c"}
    >>> rdb["my_hash"]
    {'a':'2','b':'c'}

