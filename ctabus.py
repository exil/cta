import requests

class CTABusAPI:
    base_url = 'http://www.ctabustracker.com/bustime/api/'
    api_version = 'v1'

    def __init__(self, key):
        self.key = key
        self.url = self.base_url + self.api_version + '/'

    def get_time(self):
        return self.request_cta('gettime')

    # only one arg allowed
    def get_vehicles(self, vehicle_ids=None, routes=None):
        args = locals().copy()
        return self.request_cta('getvehicles', args)
        
    def get_routes(self):
        return self.request_cta('getroutes')

    def get_directions(self, rt):
        args = locals().copy()
        return self.request_cta('getdirections', args)

    def get_stops(self, rt=None, dir=None):
        args = locals().copy()
        return self.request_cta('getstops', args)

    def get_patterns(self, pid=None, rt=None):
        args = locals().copy()
        return self.request_cta('getpatterns', args)

    def get_predictions(self, stpid, rt, vid, top):
        return

    def get_service_bulletins(rt, rtdir, stpid):
        return

    def request_cta(self, function, args={}):
        params = {}
        params['key'] = self.key
        
        for k, v in args.iteritems():
            if (v is None or k != 'self'):
                params[k] = v

        request_url = self.url + '/' + function
        r = requests.get(request_url, params=params)
        return r.text

class Route:
    def __init__(self, id, name, direction=None, stop_ids=None):
        self.id = id        
        self.name = name
        self.direction = direction
        self.stop_ids = stop_ids

class Stop:
    def __init__(self, id, name, lat, lon, route_ids=None):
        self.id = id
        self.name = name
        self.lat = lat
        self.lon = lon
        self.route_ids = route_ids