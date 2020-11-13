#!/usr/bin/python3.6
import os
os.environ['VITA_CONFIG'] = '/var/www/config.py'
import sys
# Add the ptdraft folder path to the sys.path list
sys.path.append('/var/www/pharmex')

import asyncio


from manufacturer.ManufacturerClient import ManufacturerClient
from modules.vita.warehouse.ProductsExecutorClient import ProductsExecutorClient


async def test():
    manufacturer = ManufacturerClient()
    result = await manufacturer.add(name="Гедеон")
    print("added ")
    print(result)
    result = await manufacturer.remove(name="Гедеон")
    print("removed ")
    print(result)


async def cycle():
    product_client = ProductsExecutorClient()
    products = await product_client.get_all()
    manufacturer = ManufacturerClient()
    for pid, product in products.items():
        print(product)
        result = await manufacturer.add(name=product["manufacturer"])
        print(result)
    print("finished")


loop = asyncio.get_event_loop()
loop.run_until_complete(cycle())
