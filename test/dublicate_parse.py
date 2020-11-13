# region import
import sys
import os  # NOQA: E402
os.environ['VITA_CONFIG'] = '/var/www/config.py'  # NOQA: E402
from collections import OrderedDict


sys.path.append(os.path.abspath(__file__ + "/../../"))  # NOQA: E402
sys.path.append(os.path.abspath(__file__ + "/../../modules/vita"))  # NOQA: E402
sys.path.append(os.path.abspath(__file__ + "/../../modules/business"))  # NOQA: E402

from suppliers.aliases.AgentProductAliasesClient import AgentProductAliasesClient
from suppliers.aliases.AgentFullAliasesClient import AgentFullAliasesClient
from warehouse.ProductsExecutorClient import ProductsExecutorClient
import pandas
import math

import asyncio


async def parse():
    first_file = "/var/www/duplicate_finder_mustafo.xlsx"
    df = pandas.read_excel(first_file, header=None)
    df = df.applymap(lambda x: x.strip() if type(x) is str else x)
    df = df.replace('  ', ' ', regex=True)
    first = df.to_dict(orient='records', into=OrderedDict)
    has = set()
    count = 0
    product_client = ProductsExecutorClient()
    for item in first:
        try:
            if not math.isnan(float(item[3])):
                product_id = int(item[4])
                origin_id = int(item[3])
                print(str(product_id) + " " + item[5]
                      + " is dublicate for " + str(origin_id))
                count += 1

                alias_client = AgentProductAliasesClient()
                aliases = await alias_client.list_by_product_id(product_id=product_id)
                origin_product = await product_client.get_one(product_id=origin_id)
                for alias in aliases:
                    alias["product_id"] = origin_id
                    await alias_client.modify(data=alias, filter=alias["alias_id"])

                full_alias_client = AgentFullAliasesClient()
                full_aliases = await full_alias_client.list_by_product_id(product_id=product_id)
                for alias in full_aliases:
                    alias["product_id"] = origin_id
                    await full_alias_client.modify(data=alias, filter=alias["alias_id"])

                await product_client.remove(data={"product_id": product_id})
                print("remove product with id = " + str(product_id))

        except:
            import traceback
            traceback.print_exc()
            pass
    print("found " + str(count) + " dublicates")


async def single_replace():
    product_client = ProductsExecutorClient()
    product_id = 7159
    origin_id = 7158
    print(str(product_id) +
          " is dublicate for " + str(origin_id))

    alias_client = AgentProductAliasesClient()
    aliases = await alias_client.list_by_product_id(product_id=product_id)
    origin_product = await product_client.get_one(product_id=origin_id)
    for alias in aliases:
        alias["product_id"] = origin_id
        await alias_client.modify(data=alias, filter=alias["alias_id"])

    full_alias_client = AgentFullAliasesClient()
    full_aliases = await full_alias_client.list_by_product_id(product_id=product_id)
    for alias in full_aliases:
        alias["product_id"] = origin_id
        await full_alias_client.modify(data=alias, filter=alias["alias_id"])

    await product_client.remove(data={"product_id": product_id})
    print("remove product with id = " + str(product_id))
asyncio.get_event_loop().run_until_complete(single_replace())
