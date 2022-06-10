from itertools import zip_longest
import json
from unittest import result
from tile38_helper import tile38_helper
import db
import tile38
import asyncio
from redis_helper import redis_helper
from pydantic import BaseModel
import time

async def start_updating():
    while True:
        start_time = round(time.time() * 1000)
        await update()
        end_time = round(time.time() * 1000)
        print("Updating stops took", end_time - start_time, "ms")
        time.sleep(30)

async def update():
    stops = db.get_all_stops_from_db()
    with redis_helper.get_resource() as r:
        # Count vehicles
        pipe = r.pipeline()
        count_results = []
        for stop in stops:
            result = await tile38.get_vehicles(stop.area)
            stop.num_vehicles_available = count_modes(result=result)
            pipe.get("stop:" + stop.stop_id + ":status")
        res = pipe.execute()

        # Determine new state.
        for index, stop in enumerate(stops):
            old_state = res[index]
            if old_state  == None:
                old_state = get_initial_state(stop.capacity)
            new_state = calculate_available_places(stop.capacity, stop.num_vehicles_available)
            stop.num_places_available = new_state
            determine_state_change(stop.capacity, old_state, new_state)

        store_stops(r, stops)
        

def store_stops(r, stops):
    pipe = r.pipeline()
    pipe.set("stops_last_updated", round(time.time() * 1000))
    for stop in stops:
        pipe.setex("stop:" + stop.stop_id, 300, stop.json())
        pipe.sadd("all_stops", stop.stop_id)
        pipe.sadd("stops_per_municipality:" + stop.municipality, stop.stop_id)
    pipe.execute()

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

def calculate_available_places(capacity, counted_vehicles):
    if "combined" in capacity:
        return calculate_places_available_combined(capacity["combined"], counted_vehicles)
    return calculate_places_available_per_mode(capacity, counted_vehicles)


def calculate_places_available_per_mode(capacity, counted_vehicles):
    places_available = {
        "moped": 0,
        "cargo_bicycle": 0,
        "bicycle": 0,
        "car": 0,
        "other": 0
    }
    # Add other temporarily to moped as long gosharing is not delivering correct data.
    if "other" in counted_vehicles:
        counted_vehicles["moped"] += counted_vehicles["other"]
    for mode, vehicles_capacity in capacity.items():
        if mode in ["combined", "other"]:
            continue
        elif mode not in counted_vehicles:
            places_available[mode] = vehicles_capacity
        else:
            places_available[mode] = max(vehicles_capacity - counted_vehicles[mode], 0)
    return places_available

def calculate_places_available_combined(combined_capacitiy, counted_vehicles):
    total = 0
    modes_to_include_in_combined = ["moped", "cargo_bicycle", "bicycle", "other"]
    for mode in modes_to_include_in_combined:
        if mode in counted_vehicles:
            total += counted_vehicles[mode]
    
    places_available = {
        "moped": 0,
        "cargo_bicycle": 0,
        "bicycle": 0,
        "car": 0,
        "other": 0
    }
    if total >= combined_capacitiy:
        return places_available

    available_space = combined_capacitiy - total
    for mode in modes_to_include_in_combined:
        places_available[mode] = available_space
                
    return places_available


def get_current_vehicles():
    pass

def get_initial_state(capacity):
    state_per_mode = {
        "moped": -1,
        "cargo_bicycle": -1,
        "bicycle": -1,
        "car": -1,
        "other": -1
    }
    for key, value in capacity.items():
        if key in state_per_mode and value == 0:
            state_per_mode[key] = 0
        if key == "combined" and value == 0:
            return {
                "moped": 0,
                "cargo_bicycle": 0,
                "bicycle": 0,
                "car": 0,
                "other": 0
            }
    return state_per_mode

class StateChange(BaseModel):
    opened: list[str] = []
    closed: list[str] = []

def determine_state_change(capacity, old_state, new_state):
    state_changes = StateChange()
    for mode, old_value in old_state.items():
        new_value = new_state[mode]
        if mode not in new_state:
            state_changes.closed.append(mode)
        elif old_value > 0 and new_value == 0:
            state_changes.closed.append(mode)
        elif old_value == 0 and new_value > 0:
            state_changes.opened.append(mode)


asyncio.run(start_updating())
  


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
