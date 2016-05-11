# -*- coding: utf-8 -*-
import logging

import settings
from fetch_latlng import AddrLatlngUtil
from district import District 


class DistrictExtract(object):
    def __init__(self, mapfile=None, cfgfile=None):
        self.district = District(mapfile=mapfile, cfgfile=cfgfile)
        self.addr_latlng = AddrLatlngUtil()

    def extract_district(self, cid, coord_lst, addr, location):
        districts = []
        cities = []
        if coord_lst:
            if not addr:
                addr = u''
            for coord in coord_lst:
                lat = coord[0]
                lng = coord[1]
                if settings.FETCH_DISTRICT.get(cid, 0):
                    lat, lng = self.addr_latlng.coord_google_to_baidu(lat, lng)
                district_name, min_distance = self.district.min_distance_district(addr, lat, lng)
                if district_name:
                    districts.append(district_name)
                    end_pos = district_name.find(u'$')
                    if end_pos == -1:
                        cities.append(district_name)
                    else:
                        cities.append(district_name[0:end_pos])
                else:
                    logging.error('no district: %s, %s, %s', cid, lat, lng)
        elif addr:
            addresses = addr.split(u',')
            if location and len(location) > 0 and len(location[0]) < 6:
                city = location[0]
                if city == u'全国':
                    city = u''
            else:
                city = u''

            for address in set(addresses):
                # logging.debug('addr: %s', address)
                district_name, min_distance = self.district.get_district(address, city)
                if district_name:
                    # logging.debug('district: %s, %s', cid, district_name)
                    districts.append(district_name)
                    end_pos = district_name.find(u'$')
                    if end_pos == -1:
                        cities.append(district_name)
                    else:
                        cities.append(district_name[0:end_pos])
                else:
                    logging.error('no district: %s, %s', cid, address)

        return districts, cities

    def test(self):
        cid = u"Cjinshan"
        location = [u"襄阳"]
        addr = u"檀溪路图书馆对面农行侧对面（人才市场附近门面）,长虹路民发城市印象一号楼601室"
        coord_lst = []
        districts, cities = self.extract_district(cid, coord_lst, addr, location)
        print u" ".join(districts)
        print u" ".join(cities)

if __name__ == "__main__":
    de = DistrictExtract()
    de.test()

