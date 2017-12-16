#!/usr/bin/python
from bottle import route, run, template, get, debug, TEMPLATES
import sqlite3

debug(True)

@route('/')
def thing():
    routes = []
    conn = sqlite3.connect('cta.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    for row in c.execute("SELECT id, name, direction FROM routes"):
        route = {'id': row['id'], 'name': row['name'], 'direction': row['direction']}
        routes.append(route)

    return template('cta', routes=routes)

@route('/routes', method='GET')
def get_all_routes():
    json = {}
    json['routes'] = []
    conn = sqlite3.connect('cta.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    for row in c.execute("SELECT id, name, direction FROM routes"):
        route = {'id': row['id'], 'name': row['name'], 'direction': row['direction']}
        json['routes'].append(route)
    
    c.close()

    return json    

@route('/routes/stop/:stop_id', method='GET')
def get_routes_by_stop(stop_id):
    json = {}
    json['routes'] = []
    conn = sqlite3.connect('cta.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    for row in c.execute("SELECT s.id stop_id, s.name stop_name, s.latitude, s.longitude, r.id route_id, r.name route_name, r.direction from routes_stops as rs inner join stops as s on rs.stop_id = s.id inner join routes as r on rs.route_id = r.id and rs.direction = r.direction where rs.stop_id=?", (stop_id,)):
        json['stopId'] = row['stop_id']
        json['stopName'] = row['stop_name']
        
        route = {'id': row['route_id'], 'name': row['route_name'], 'direction': row['direction']}
        json['routes'].append(route)
    
    c.close()
    return json

@route('/patterns/route/:route_id/direction/:direction', method='GET')
def get_patterns_and_stops_by_route(route_id, direction):
    json = {}
    json['patterns'] = []
    pattern_count = -1
    current_pattern = None

    conn = sqlite3.connect('cta.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    for row in c.execute("SELECT p.pattern_id, p.stop_id, s.name stop_name, p.latitude, p.longitude FROM patterns as p LEFT OUTER JOIN stops as s on p.stop_id = s.id WHERE p.route_id = ? AND p.direction = ?", (route_id, direction)):
        # a route may have more than one pattern.
        if (current_pattern != row['pattern_id']):
            current_pattern = row['pattern_id']
            pattern_count = pattern_count + 1
            json['patterns'].append({'stops': [], 'pattern': []})

        if (row['stop_id'] is not None):
            stop = {'stopId': row['stop_id'], 'stopName': row['stop_name']}
            json['patterns'][pattern_count]['stops'].append(stop)

        pattern = {'latitude': row['latitude'], 'longitude': row['longitude']}
        json['patterns'][pattern_count]['pattern'].append(pattern)
    
    c.close()
    return json

run(reloader=True)