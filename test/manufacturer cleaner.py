# region import
import sys
import os  # NOQA: E402
os.environ['VITA_CONFIG'] = '/var/www/config.py'  # NOQA: E402
from collections import OrderedDict


sys.path.append(os.path.abspath(__file__ + "/../../"))  # NOQA: E402
sys.path.append(os.path.abspath(__file__ + "/../../modules/vita"))  # NOQA: E402
sys.path.append(os.path.abspath(__file__ + "/../../modules/business"))  # NOQA: E402

from suppliers.aliases.AgentManufacturerAliasesClient import AgentManufacturerAliasesClient
from warehouse.manufacturer.ManufacturerClient import ManufacturerClient
from modules.kinetic_core.Connector import db
import pandas
import math

import asyncio


async def parse():
    results = await db.list("select manufacturer_id from manufacturers where manufacturer_id not in (select manufacturer_id from products)")
    has = set()
    count = 0
    manufacturer_client = ManufacturerClient()
    for result in results:
        manufacturer_id = result["manufacturer_id"]
        print(manufacturer_id)
        alias_client = AgentManufacturerAliasesClient()
        aliases = await alias_client.list_by_manufacturer_id(manufacturer_id=manufacturer_id)
        origin_product = await manufacturer_client.get_by_id(mid=manufacturer_id)
        for alias in aliases:
            await alias_client.remove(alias_id=alias["alias_id"])

        await manufacturer_client.remove_by_id(manufacturer_id=manufacturer_id)
        print("remove manufacturer with id = " + str(manufacturer_id))

    print("found " + str(count) + " dublicates")


asyncio.get_event_loop().run_until_complete(parse())
