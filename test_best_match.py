#!/usr/bin/python3.6
import os
os.environ['VITA_CONFIG'] = '/var/www/config.py'
import asyncio
import traceback
from datetime import datetime
import sys, os
from elasticsearch_async import AsyncElasticsearch
sys.path.append(os.path.abspath(__file__ + "/../"))
from dataclerk.DataClerkClient import DataClerkClient
from modules.business.warehouse.ProductsExecutorClient import ProductsExecutorClient
from manufacturer.ManufacturerClient import ManufacturerClient

es = AsyncElasticsearch(hosts=['34.247.32.113'],
    http_auth=('vita', 'g6t7y7h98hyg67'),port=8080)
async def main(loop):
    es.indices.delete(index='productsexecutor-index')
    product_client = ProductsExecutorClient()
    print("best_match")
    products = await product_client.get_all()
    #result = await picker.best_matches(name="Калгель гель 33% 10г".lower())
    
    manufacturer_client = ManufacturerClient()
    for pid, product in products.items():
        if product["manufacturer"] is not None:
            manufacturer = await manufacturer_client.get_by_name(name=product["manufacturer"].lower())
            result = await product_client.modify({
                "manufacturer_id": manufacturer["manufacturer_id"],
                "product_id": product["product_id"]
                })
            print(result)

loop = asyncio.get_event_loop()

result = loop.run_until_complete(main(loop))
