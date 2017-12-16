# gets buses with more than one pattern

import sqlite3

conn = sqlite3.connect('cta.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

count = 0
cur = '1'

for row in c.execute("select pattern_id, route_id, direction from patterns where sequence = 1"):
    if row['route_id'] == cur:
        count = count + 1
    else:
       count = 1

    if count > 2 and count < 4:
        print str(row['route_id'])

    cur = row['route_id']

banana = []
for row in c.execute("select latitude, longitude from patterns where route_id = 20 AND direction = 'West Bound'"):
    banana.append([row['latitude'], row['longitude']])


