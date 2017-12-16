#!/usr/bin/python

# This is how the data gets created.

# Data is first pulled from API and put into XML files.
# That data is then read from the XML files and put into the database.

from ctabus import CTABusAPI, Route, Stop
import xml.etree.ElementTree as ET
import os, re, environ, sqlite3

key = os.environ.get('KEY','')
cta = CTABusAPI(key)
conn = sqlite3.connect('cta.db')
sql_cta = conn.cursor()

# ALL ROUTES and ALL STOPS
ALL_ROUTES = {}
ALL_STOPS = {}

#todo: only use database

def populate_data():
    populate_all()

    conn.close()

    #for route in routes:
    #    print route.id, route.name, route.direction

    #print_stops()

def print_routes():
    for key in sorted(ALL_ROUTES.iterkeys(), key=_order):
        route = ALL_ROUTES[key]
        print key, route.name, route.direction

def print_stops():
    for key in sorted(ALL_STOPS.iterkeys(), key=_order):
        stop = ALL_STOPS[key]
        print key, stop.name, stop.route_ids, '\n'

def populate_all():
    route_xml = create_routes_xml_file()

    tree = ET.parse(route_xml)
    root = tree.getroot()

    for dom_route in root.findall('route'):
        route_id_el = dom_route.find('rt')
        route_name_el = dom_route.find('rtnm')

        if (route_id_el is not None and route_name_el is not None):
            route_id = route_id_el.text
            route_name = route_name_el.text

            direction_els = get_direction(route_id)

            populate_patterns(route_id)

            # add route(s)
            for direction_el in direction_els:
                direction = direction_el.text
                print route_id, direction
                stop_ids = populate_stops(route_id, direction)
                route = Route(route_id, route_name, direction, stop_ids)
                # add row
                sql_cta.execute("INSERT INTO routes (id, name, direction) VALUES(?, ?, ?)", (route_id, route_name, direction))
                # add row to relationship
                for stop_id in stop_ids:
                    sql_cta.execute("INSERT INTO routes_stops (route_id, direction, stop_id) VALUES(?, ?, ?)", (route_id, direction, stop_id))

                conn.commit()

                ALL_ROUTES[route_id] = route

def get_direction(route_id):
    file_name = create_direction_xml_file(route_id)
    tree = ET.parse(file_name)
    root = tree.getroot()

    return root.findall('dir')

def populate_stops(route_id, direction):
    file_name = create_stops_xml_file((route_id, direction))
    
    print file_name
    tree = ET.parse(file_name)
    root = tree.getroot()
    stop_ids = []

    for dom_stop in root.findall('stop'):
        stop_id = dom_stop.find('stpid').text
        stop_name = dom_stop.find('stpnm').text
        latitude = dom_stop.find('lat').text
        longitude = dom_stop.find('lon').text
        routes = [(route_id, direction)]

        stop_ids.append(stop_id)
        
        if (stop_id in ALL_STOPS):
            ALL_STOPS[stop_id].route_ids.append(routes)
        else:
            stop = Stop(stop_id, stop_name, latitude, longitude, routes)
            ALL_STOPS[stop_id] = stop
            # add row to stop table
            sql_cta.execute("INSERT INTO stops (id, name, latitude, longitude) VALUES(?, ?, ?, ?)", (stop_id, stop_name, float(latitude), float(longitude)))
            conn.commit()

    return stop_ids

def populate_patterns(route_id):
    file_name = create_pattern_xml_file(route_id)

    tree = ET.parse(file_name)
    root = tree.getroot()

    for ptr in root.findall('ptr'):
        pattern_id = ptr.find('pid').text
        direction = ptr.find('rtdir').text

        for pt in ptr.findall('pt'):
            sequence = pt.find('seq').text
            latitude = pt.find('lat').text
            longitude = pt.find('lon').text

            point_type_el = pt.find('typ')
            point_type = 'W'
            #pattern_id integer, direction varchar(200), route_id integer, stop_id integer, sequence integer, latitude decimal(3,6), longitude decimal(3,6), point_type char(1)
            stop_id_el = pt.find('stpid')
            stop_id = None

            if (stop_id_el is not None):
                stop_id = stop_id_el.text

            if (point_type_el is not None):
                point_type = point_type_el.text

            sql_cta.execute("INSERT INTO patterns (pattern_id, route_id, direction, stop_id, sequence, latitude, longitude, point_type) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (pattern_id, route_id, direction, stop_id, sequence, float(latitude), float(longitude), point_type))
            conn.commit()
  
def create_routes_xml_file():
    file_name = 'xml2/routes.xml'

    if os.path.exists(file_name):
        return file_name

    f = open(file_name, 'w')
    xml = cta.get_routes()

    if (len(xml)):
        f.write(xml)
    else:
        print 'error writing'
    f.close()

    return file_name

def create_direction_xml_files(route_ids):
    route_files = {}

    for route_id in route_ids:
        route_files[route_id] = create_direction_xml_file(route_id)

    return route_files

def create_direction_xml_file(route_id):
    file_name = 'xml2/directions/' + route_id + '.xml'

    if os.path.exists(file_name):
        return file_name

    f = open(file_name, 'w')

    xml = cta.get_directions(route_id)

    if (len(xml)):
        f.write(xml)
    else:
        print 'error writing'
        
    f.close()

    return file_name

def create_pattern_xml_file(route_id):
    file_name = 'xml2/patterns/' + route_id + '.xml'

    if os.path.exists(file_name):
        return file_name

    f = open(file_name, 'w')

    xml = cta.get_patterns(rt=route_id)

    if (len(xml)):
        f.write(xml)
    else:
        print 'error writing'
        
    f.close()

    return file_name

# routes - tuple with rtid and dir
def create_stops_xml_files(routes_data):
    stop_files = {}

    for route_data in routes_data:
        stop_files = create_stops_xml_file(route_data)

    return stop_files

def create_stops_xml_file(route_data):
    route_id, direction = route_data
    dir_name = 'xml2/stops/' + route_id + '/'
    file_name = direction + '.xml'
    full_path = dir_name + file_name

    if os.path.exists(full_path):
        return full_path

    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)

    f = open(full_path, 'w')
    
    xml = cta.get_stops(route_id, direction)

    if (len(xml)):
        f.write(xml)
    else:
        print 'error writing'

        
    f.close()

    return full_path

def _order(key):
    new_key = key

    if re.search('[A-Za-z]', key) is not None:
        new_key = re.sub(r'\D', '', key)

    return int(new_key)

if __name__ == "__main__":
    populate_data()