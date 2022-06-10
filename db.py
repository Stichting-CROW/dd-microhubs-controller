from db_helper import db_helper
import time
import stop

def get_all_stops_from_db():
    with db_helper.get_resource() as (cur, conn):
        try:
            rows = query_all_stops(cur)
            return list(map(convert_stop, rows))
        except Exception as e:
            conn.rollback()
            print(e)

def query_all_stops(cur):
    stmt = """
        SELECT stop_id, stops.name, 
        json_build_object(
            'type',       'Feature',
            'geometry',   ST_AsGeoJSON(location)::json,
            'properties',  json_build_object()
        ) as location,
        status, capacity, stops.geography_id as geography_id, 
        -- Add margin of 10m's to take GPS inaccuracy into account.
        json_build_object(
            'type',       'Feature',
            'geometry',   ST_AsGeoJSON(ST_Buffer(area::geography, 10))::json,
            'properties',  json_build_object()
        ) as area, municipality
        FROM geographies
        JOIN zones
        USING (zone_id) 
        JOIN stops
        USING (geography_id);
    """
    cur.execute(stmt)
    return cur.fetchall()
      
def convert_stop(row):
    return stop.MdsStop(
        stop_id=row["stop_id"],
        name=row["name"],
        last_reported = int(time.time() * 1000),
        location = row["location"],
        status = row["status"],
        capacity = row["capacity"],
        area = row["area"],
        municipality = row["municipality"],
        geography_id = row["geography_id"]
        # num_vehicles_available: Dict[str, int]
        # num_vehicles_disabled: Dict[str, int]
        # num_places_available: Dict[str, int]
    )