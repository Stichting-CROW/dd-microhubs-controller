import asyncio
from geojson_pydantic import Polygon, MultiPolygon
from stop import MdsStop
from tile38_helper import tile38_helper
import time

async def get_vehicles_in_stops(stops: list[MdsStop]):
    with tile38_helper.get_resource() as tile38_client:
        result = []
        for i in range(0, len(stops), 100):
            result.extend(
                get_vehicles_in_stops_batch(tile38_client, stops[i:i + 100])
            )
        return result

def get_vehicles_in_stops_batch(tile38_client, zones):
    start_time = time.time()
    pipe = tile38_client.pipeline(transaction=False)
    for zone in zones:
        if type(zone.area.geometry) is Polygon or type(zone.area.geometry) is MultiPolygon:
            pipe.execute_command('WITHIN', 'vehicles', 'LIMIT', '10000', 'IDS', 'OBJECT', zone.area.geometry.json())
    result = pipe.execute()
    print(f"Tile38 count batch took  {time.time() - start_time}s")
    return result
