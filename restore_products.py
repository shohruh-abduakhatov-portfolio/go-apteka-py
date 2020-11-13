#!/usr/bin/python3.6
import sys
import os
os.environ['VITA_CONFIG'] = '/var/www/config.py'
import asyncio
import traceback
from datetime import datetime
sys.path.append(os.path.abspath(__file__ + "/../"))
sys.path.append(os.path.abspath(__file__ + "/../") + "/modules/business/")
print(os.path.abspath(__file__ + "/../") + "/modules/business/")
from dataclerk.DataClerkClient import DataClerkClient
from modules.business.warehouse.ProductsExecutorClient import ProductsExecutorClient
from modules.kinetic_core.Connector import db


async def main(loop):
    products = await db.list("select product_id from products where (to_delete is null or to_delete = 0) ")
    product_client = ProductsExecutorClient()
    for product in products:
        res = await product_client.get_one(product_id=product["product_id"])
        if res is None:
            origin = await product_client.get_details(instance_id=product["product_id"])
            await product_client.modify(data=origin)
            print("failed " + str(product["product_id"]))

loop = asyncio.get_event_loop()

result = loop.run_until_complete(main(loop))
