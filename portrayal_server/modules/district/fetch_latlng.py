# -*- coding: utf-8 -*-
import urllib2
import json
import base64
import logging



class AddrLatlngUtil(object):
    def __init__(self):
        self.LATLNG_URL = 'http://api.map.baidu.com/geocoder/v2/?ak=26c9391f93ddc8bffd8919b689ab1e6b&output=json&address=%s&city=%s'
        self.ADDR_URL = 'http://api.map.baidu.com/place/v2/search?ak=26c9391f93ddc8bffd8919b689ab1e6b&output=json&query=%s&page_size=2&page_num=0&scope=1&region=全国'
        self.CONVERT_URL = 'http://api.map.baidu.com/ag/coord/convert?from=2&to=4&x=%s&y=%s'

    def json_response(self, url):
        r = urllib2.urlopen(url, timeout=0.5)
        data = r.read()
        data = json.loads(data)
        return data

    def coord_google_to_baidu(self, lat, lng):
        url = self.CONVERT_URL % (lng, lat)
        c = 0
        data = None
        while c < 3:
            try:
                data = self.json_response(url)
                break
            except:
                pass
            c += 1
        if data and data['error'] == 0:
            lng = float(base64.b64decode(data['x']))
            lat = float(base64.b64decode(data['y']))
        else:
            logging.error('convert coord failed: %s, %s', lat, lng)
        return (lat, lng)

    def fetch_latlng(self, address, city = u''):
        address = address.replace(u' ', u'')
        url = self.LATLNG_URL % (urllib2.quote(address.encode('utf-8')), city.encode('utf-8'))
        data = self.json_response(url)
        if data['status'] == 0 and ('result' in data):
            result = data['result']
        #elif city:
        #    return self.fetch_latlng(address)
        else:
            result = None
        #if not result:
        #    url = self.ADDR_URL % address.encode('utf-8')
        #    data = self.json_response(url)
        #    if 'results' in data and len(data['results']) > 0:
        #        result_0 = data['results'][0]
        #        result = result_0
        #        if 'address' in result_0:
        #            new_address = data['results'][0]['address'].replace(u' ', u'').encode('utf-8')
        #            url = self.LATLNG_URL % (new_address, city.encode('utf-8'))
        #            data = self.json_response(url)
        #            if data['status'] == 0 and ('result' in data):
        #                result = data['result']
        #        else:
        #            result = result_0
        return result
                                                                                                                                                      
if __name__ == '__main__':                                                                                                                            
    alu = AddrLatlngUtil()
    print alu.fetch_latlng(u'惠州惠东县巽寮滨海旅游度假区')
    print alu.coord_google_to_baidu(40.01818439,116.35490961)
