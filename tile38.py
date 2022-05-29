import asyncio
from tile38_helper import tile38_helper

async def get_vehicles(area):
    with tile38_helper.get_resource() as tile38:
        response = await tile38.within("vehicles").object(area.geometry).asObjects()
        return response
