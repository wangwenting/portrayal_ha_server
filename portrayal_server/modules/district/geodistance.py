from math import pi, sin, cos, atan2, sqrt

class GeoUtils(object):
    def __init__(self):
        pass

    @staticmethod
    def to_rad(angle):
        return angle / 180.0 * pi

    @staticmethod
    def geodistance(lat1, lng1, lat2, lng2):
        R = 6371
        lat1 = GeoUtils.to_rad(lat1)
        lng1 = GeoUtils.to_rad(lng1)
        lat2 = GeoUtils.to_rad(lat2)
        lng2 = GeoUtils.to_rad(lng2)
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = sin(dlat/2) * sin(dlat/2) + sin(dlng/2) * sin(dlng/2) * cos(lat1) * cos(lat2)
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        d = R * c
        return d
