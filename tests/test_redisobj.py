import unittest
import mock

import redisobj


class TestRedisDB(unittest.TestCase):
    @mock.patch("redis.StrictRedis")
    def setUp(self, redis_conn):
        self.rdb = redisobj.RedisDB()
        self.mock_db = redis_conn.return_value

    def test_repr(self):
        self.assertEquals(str(self.rdb), "<RedisDB host:'localhost' port:'6379' db:'0' >")


    def test_contains(self):
        # mock redis' exists method
        mock_exists_results = [True, False]
        self.mock_db.exists.side_effect = lambda k: mock_exists_results.pop(0)

        # test in-operator uses redis' exists method
        self.assertTrue("test_key1" in self.rdb)
        self.assertFalse("test_key2" in self.rdb)


    def test_get_item(self):
        # mock redis' exists & get method
        self.mock_db.exists.return_value = True

        # test __getitem__ strings
        self.mock_db.type.return_value = "string"
        mock_get_results = ["1", "2"]
        self.mock_db.get.side_effect = lambda k: mock_get_results.pop(0)

        for k, v in (("test_key1", "1"), ("test_key2", "2")):
            self.assertEqual(self.rdb[k], v)
            self.assertTrue(('get', (k,), {}) in self.mock_db.method_calls)

        # test __getitem__ lists
        self.mock_db.type.return_value = "list"
        mock_lrange_results = [['a','b','c'], ['1','2','3']]
        self.mock_db.lrange.side_effect = lambda k,i,j: mock_lrange_results.pop(0)

        for k, v in (("test_list1", ['a','b','c']), ("test_list2", ['1','2','3'])):
            self.assertEqual(self.rdb[k], v)
            self.assertTrue(('lrange', (k,0,-1), {}) in self.mock_db.method_calls)

        # test __getitem__ sets
        self.mock_db.type.return_value = "set"
        mock_smembers_results = [set(['a','b','c']), set(['1','2','3'])]
        self.mock_db.smembers.side_effect = lambda k: mock_smembers_results.pop(0)

        for k, v in (("test_set1", set(['a','b','c'])), ("test_set2", set(['1','2','3']))):
            self.assertEqual(self.rdb[k], v)
            self.assertTrue(('smembers', (k,), {}) in self.mock_db.method_calls)

        # test __getitem__ hash
        self.mock_db.type.return_value = "hash"
        mock_hgetall_results = [{'a':'b','c':'d'}, {'a':'1','2':'3'}]
        self.mock_db.hgetall.side_effect = lambda k: mock_hgetall_results.pop(0)

        for k, v in (("test_hash1", {'a':'b','c':'d'}), ("test_hash2", {'a':'1','2':'3'})):
            self.assertEqual(self.rdb[k], v)
            self.assertTrue(('hgetall', (k,), {}) in self.mock_db.method_calls)


    def test_set_item(self):
        # test __setitem__ strings
        for k, v in (("test_key1", "3"), ("test_key2", "4")):
            self.rdb[k] = v
            self.assertTrue(('set', (k,v), {}) in self.mock_db.method_calls)

        # test __setitem__ lists
        self.mock_db.get.return_value = True
        self.mock_db.delete.return_value = True
        self.mock_db.type.return_value = "list"

        for k, v in (("test_list1", ['d','e','f']), ("test_list2", [4,5,6])):
            self.rdb[k] = v
            for i in v:
                self.assertTrue(('rpush', (k,i), {}) in self.mock_db.method_calls)

        # test __setitem__ sets
        for k, v in (("test_set1", set(['d','e','f'])), ("test_set2", set(['4','5','6']))):
            self.rdb[k] = v
            for i in v:
                self.assertTrue(('sadd', (k,i), {}) in self.mock_db.method_calls)

        # test __setitem__ hash
        for k, v in (("test_hash1", {'e':'f','g':'h'}), ("test_hash2", {'b':2,'3':4})):
            self.rdb[k] = v
            self.assertTrue(('hmset', (k,v), {}) in self.mock_db.method_calls)

    def test_del_item(self):
        # test __delitem__
        self.mock_db.get.return_value = True
        self.mock_db.delete.return_value = True
        self.mock_db.exists.return_value = True
        self.mock_db.type.return_value = "string"

        del self.rdb["key"]
        self.assertTrue(('delete', ("key",), {}) in self.mock_db.method_calls)


    def test_keys(self):
        # test key-retrieval
        self.mock_db.keys.return_value = ["key1", "key2"]
        self.assertEquals(self.rdb.keys(), ["key1", "key2"])
        self.assertTrue(('keys', (), {}) in self.mock_db.method_calls)


    def test_clear(self):
        # test clear
        self.rdb.clear()
        self.assertTrue(('flushdb', (), {}) in self.mock_db.method_calls)


    def test_keyerrors(self):
        self.mock_db.exists.return_value = False
        self.assertRaises(KeyError, lambda key: self.rdb[key], 'invalid_key')

    def test_invalid_data_types(self):
        # helper functions
        def set_key(key, value): self.rdb[key] = value
        def get_key(key): return self.rdb[key]
        def del_key(key): del self.rdb[key]

        # invalid key data type
        self.assertRaises(redisobj.InvalidDataType, set_key, 1, "test")
        self.assertRaises(redisobj.InvalidDataType, get_key, 1)
        self.assertRaises(redisobj.InvalidDataType, del_key, 1)

        # invalid lists data type
        self.assertRaises(redisobj.InvalidDataType, set_key, "valid_key", [1,2,[]])
        self.assertRaises(redisobj.InvalidDataType, set_key, "valid_key", [1,2,set([])])
        self.assertRaises(redisobj.InvalidDataType, set_key, "valid_key", [1,2,{}])

        # invalid sets hash type
        self.assertRaises(redisobj.InvalidDataType, set_key, "valid_key", {1:'a'})
        self.assertRaises(redisobj.InvalidDataType, set_key, "valid_key", {1:['a']})
        self.assertRaises(redisobj.InvalidDataType, set_key, "valid_key", {1:{'a':2}})

