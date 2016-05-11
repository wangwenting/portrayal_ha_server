# -*- coding: utf-8 -*-
import redis
import logging


class RedisClient(object):
    def __init__(self, host="localhost", port=6379, db=1):
        pool = redis.ConnectionPool(host=host, port=port, db=db)
        self.redis_client = redis.Redis(connection_pool=pool)
        logging.info("init redis OK ")

    def address_save_to_cache(self, address, data):
        address = address.strip()
        try:
            key = address.encode('utf-8')
        except Exception,e:
            raise e
        return self.redis_client.set(key, data)

    def address_fetch_from_cache(self, address):
        address = address.strip()
        key = address.encode('utf-8')
        return self.redis_client.get(key)

if __name__ == '__main__':
    rc = RedisClient(host="localhost")
    data = "{'a':1, 'b':2}"
    rc.address_save_to_cache('test', data)
    print rc.address_fetch_from_cache('test')
