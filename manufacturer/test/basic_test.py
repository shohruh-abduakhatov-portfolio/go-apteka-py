#!/usr/bin/python3.6

import asyncio

from manufacturer.ManufacturerClient import ManufacturerClient


async def cycle():
    manufacturer = ManufacturerClient()
    result = await manufacturer.add(name="Гедеон")
    print("added ")
    print(result)
    result = await manufacturer.remove(name="Гедеон")
    print("removed ")
    print(result)


loop = asyncio.get_event_loop()
loop.run_until_complete(cycle())
