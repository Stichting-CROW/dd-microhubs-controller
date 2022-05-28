import asyncio
from pyle38 import Tile38
import json


async def main():
    tile38 = Tile38(url="redis://localhost:9851")

    geojson = """{
            "type": "Polygon",
            "coordinates": [
            [
                [
                4.469311237335205,
                51.924446300372246
                ],
                [
                4.467165470123291,
                51.92401622751315
                ],
                [
                4.467455148696899,
                51.9235464509121
                ],
                [
                4.469418525695801,
                51.923989761356445
                ],
                [
                4.469311237335205,
                51.924446300372246
                ]
            ]
            ]
        }"""
    geojson = json.loads(geojson)
    await tile38.set("fleet", "truck").point(52.25,13.37).exec()
    response = await tile38.within("vehicles").object(geojson).asObjects()
    print(response.dict())


asyncio.run(main())
#  select st_asgeojson(st_buffer(area::geography, 10)) from zones where zone_id = 51297;