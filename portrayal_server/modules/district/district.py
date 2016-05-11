# -*- coding: utf-8 -*-
import sys, time, logging, traceback, os
import MySQLdb, ConfigParser

from redis_client import RedisClient
from fetch_latlng import AddrLatlngUtil
from geodistance  import GeoUtils
from GeoCoordinate_pb2 import GeoCoordinate

# 序列化成probuf存入redis 作为缓存


class District(object):
    def __init__(self, mapfile=None, cfgfile=None):
        # host = "192.168.61.77"
        # self.init_mysql(host=host,user="bfdroot",passwd="qianfendian",db="BfdLocation",charset="utf8")
        cur_dir = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
        if not mapfile:
            mapfile = cur_dir + "/resource/MAP_DISTRICT"
        self.init_file(mapfile)
        if not cfgfile:
            cfgfile = cur_dir + "/resource/district.conf"

        cf = ConfigParser.ConfigParser()
        cf.read(cfgfile)
        host = cf.get("redis", "host")
        port = cf.getint("redis", "port")
        db = cf.getint("redis", "db")
        self.redis_client = RedisClient(host=host, port=port, db=db)
        self.addr_latlng_util = AddrLatlngUtil()
        

    def init_mysql(self, host, user, passwd, db, charset='utf8'):
        logging.info("connect to mysql...")
        conn=MySQLdb.connect(host=host,user="bfdroot",passwd="qianfendian",db="BfdLocation",charset="utf8")
        cursor = conn.cursor()
        cursor.execute('select id, name, latitude, longitude from locations where has_child=0')   
                 
        locations = []
        location = cursor.fetchone()
        while location:
            if location[2] and location[3]:
                name = location[1]
                if type(name) is str:
                    name = name.decode('utf-8')
                id = location[0]
                latitude = location[2]
                longitude = location[3]
                locations.append( (id, name, latitude, longitude) )
            location = cursor.fetchone()

        self.locations = locations
        conn.close()
        cursor.close()

    def init_file(self, filename):
        logging.info("read district file...")
  
        rfile = open(filename, 'r')   
 
        locations = []
        line = rfile.readline()
        while line:
            location = line.split('\t')
            if location[2] and location[3]:
                name = location[1]
                if type(name) is str:
                    name = name.decode('utf-8')
                id = int(location[0])
                latitude = float(location[2])
                longitude = float(location[3])
                locations.append((id, name, latitude, longitude))
            line = rfile.readline()

        self.locations = locations
        rfile.close()

    def min_distance_district(self, address, lat, lng):
        address = address.replace(u' ', u'')
        min_distance = 20
        district = None
        for loc in self.locations:
            latitude = loc[2]
            longitude = loc[3]
            distance = GeoUtils.geodistance(lat, lng, latitude, longitude)
            if distance < min_distance:
                min_distance = distance
                district = loc

        name = u''
        if district:
            name = district[1]
        if address:
            coordinate = GeoCoordinate()
            coordinate.latitude = lat
            coordinate.longitude = lng
            if district:
                coordinate.district = district[1]
                coordinate.distance = min_distance
                logging.info('write to redis, address: %s', address)
                self.redis_client.address_save_to_cache(address, coordinate.SerializeToString())
        return name, min_distance

    def get_district(self, address, city):
        address = address.replace(u' ', u'')
        if address == u'全国':
            return None, 0

        value = self.redis_client.address_fetch_from_cache(address)
        if value:
            logging.info('found address in redis: %s', address)
            coordinate = GeoCoordinate()
            coordinate.ParseFromString(value)
            if coordinate.district:
                return coordinate.district, coordinate.distance

        result = None
        try:
            result = self.addr_latlng_util.fetch_latlng(address, city)
        except Exception, e:
            logging.error('fetch_latlng except: %s', traceback.format_exc())
        if not result or 'location' not in result:
            if city:
                return self.get_district(address, u'')
            else:
                logging.error('address: %s has no result', address)
                return None, 0
        lat = result['location']['lat']
        lng = result['location']['lng']
        result = self.min_distance_district(address, lat, lng)
        if not result:
            return None, 0
        new_city = None
        end_pos = result[0].find(u'$')
        if end_pos == -1:
            new_city = result[0]
        else:
            new_city = result[0][0:end_pos]
        check = False
        for c in city:
            if ord(c) > 256:
                check = True
        if check and city.find(new_city) == -1:
            logging.warn('city not match: %s, orig: %s', result[0], city)
            return None, 0
        logging.info('address-to-district: %s, %s, %s, %s, %f', address, lat, lng, result[0], result[1])
        return result


if __name__ == '__main__':
    dis = District() 
    #district_name, min_distance = dis.min_distance_district('', 23.8263047258, 114.246362579)
    district_name, min_distance = dis.min_distance_district(u'上海浦东新区泥城镇泥城路149弄3号', 30.906018457239, 121.8294444033)
    #district_name, min_distance = dis.get_district(u'上海浦东新区泥城镇泥城路149弄3号', u'上海')
    print min_distance
    print district_name
