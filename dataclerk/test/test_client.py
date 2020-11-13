#!/usr/bin/python3.6

import asyncio
import traceback
from datetime import datetime
import sys,os
sys.path.append(os.path.abspath(__file__ + "/../../../modules/business/"))
sys.path.append(os.path.abspath(__file__ + "/../../../"))

from warehouse.ProductsExecutorClient import ProductsExecutorClient

async def get_one():

    product_client = ProductsExecutorClient()
    product = await product_client.get_one_name(data={"name": "Ультран 2мл №5"})
    print(product)

loop = asyncio.get_event_loop()
loop.run_until_complete(get_one())