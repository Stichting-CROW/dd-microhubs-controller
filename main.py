from itertools import zip_longest
import json
from unittest import result
from tile38_helper import tile38_helper
import db
import tile38
import asyncio

async def update():
    stops = db.get_all_stops_from_db()
    for stop in stops:
        result = await tile38.get_vehicles(stop.area)
        print(stop.name)
        print(count_modes(result))
        

def count_modes(result):
    vehicles_available = {
        "moped": 0,
        "cargo_bicycle": 0,
        "bicycle": 0,
        "car": 0,
        "other": 0
    }
    for vehicle in result.objects:
        mode = vehicle.id.split(":")[2]
        if mode in vehicles_available:
            vehicles_available[mode] += 1
        else:
            vehicles_available["other"] += 1
    return vehicles_available

def calculate_places_available_per_mode(capacity, counted_vehicles):
    total = 0
    for mode, vehicles_capacity in counted_vehicles:
        if mode == "combined":
            continue
        if mode in counted_vehicles:
            counted_vehicles[mode] < vehicles_capacity

# def calculate_places_available_combined(capacity, counted_vehicles):
#     total = 0
#     vehicles_available = {
#         "moped": 0,
#         "cargo_bicycle": 0,
#         "bicycle": 0,
#         "car": 0,
#         "other": 0
#     }
#     for _, vehicles_capacity in counted_vehicles:
#         total += vehicles_capacity
#     counted_vehicles[]



asyncio.run(update())


#  select st_asgeojson(st_buffer(area::geography, 10)) from zones where zone_id = 51297;

# Haal alle park stops op:
#
# SELECT stop_id, stops.name, ST_X(location) as stop_lng, ST_Y(location) stop_lat, capacity, stops.geography_id, ST_AsGeoJSON(
#     ST_Buffer(area::geography, 10)
# ) as area
# FROM geographies
# JOIN zones
# USING (zone_id) 
# JOIN stops
# USING (geography_id);
# # Bepaal per stop hoeveel voertuigen er in die zone staan.
# tile38 trucje

# Haal per stop op wat de vorige status was.  
# Wanneer het aantal voertuigen in de stop >= capaciteit sluit stop.
# 1. combined.
# 2. per modaliteit.
# Wanneer hub gesloten en het aantal voertuigen in de stop < 0.95 * capaciteit open hub.

# Wanneer status hub veranderd, stuur email.

# Sla stop opbject op in redis met alle logische parameters. 
# Sla stopId op in list van stops per gemeente en landelijk. 
