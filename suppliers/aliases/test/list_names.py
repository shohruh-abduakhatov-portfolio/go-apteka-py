import asyncio  # NOQA: E402
import os  # NOQA: E402
import sys  # NOQA: E402
os.environ['VITA_CONFIG'] = '/var/www/config.py'  # NOQA: E402

sys.path.append(os.path.abspath(__file__ + "/../../../../"))  # NOQA: E402
sys.path.append(os.path.abspath(__file__ + "/../../../../modules/business/"))  # NOQA: E402
print(os.path.abspath(__file__ + "/../../../../"))  # NOQA: E402

from suppliers.aliases.AgentManufacturerAliasesClient import AgentManufacturerAliasesClient
from warehouse.ProductsExecutorClient import ProductsExecutorClient

from warehouse.manufacturer.ManufacturerClient import ManufacturerClient
from modules.kinetic_core.Connector import db


async def list_names():
    agent_manufacturers_client = AgentManufacturerAliasesClient()
    manufacturer_aliases = await agent_manufacturers_client.list_names(agent_id=10)
    print(manufacturer_aliases)
    pass


async def change_alias_manufacturer_id():
    m_client = AgentManufacturerAliasesClient()
    manufacturer_aliases = await m_client.modify(data={
        "manufacturer_id": 18597,
        "origin": "world medicine"}, filter=3644)
    print(manufacturer_aliases)
    pass


async def remove_alias():
    m_client = AgentManufacturerAliasesClient()
    manufacturer_aliases = await m_client.remove(alias_id=6742)
    print(manufacturer_aliases)
    pass


async def clean():
    manufacturer_client = ManufacturerClient()
    dublicates = await db.list("select * from manufacturers as ou where (select count(*) from manufacturers as inr where inr.name = ou.name) > 1 order by name desc")
    name = None
    origin_id = 0
    counter = 0
    for dublicate in dublicates:
        if name is None:
            name = dublicate["name"]
            origin_id = dublicate["manufacturer_id"]
        elif name == dublicate["name"]:
            counter += 1
            manufacturer_id = dublicate["manufacturer_id"]
            alias_client = AgentManufacturerAliasesClient()
            aliases = await alias_client.list_by_manufacturer_id(manufacturer_id=manufacturer_id)
            print("### ALIASES ###")
            print(aliases)
            print("### END ###")

            for alias in aliases:
                alias["manufacturer_id"] = origin_id
                manufacturer_aliases = await alias_client.modify(data=alias,
                                                                 filter=alias["alias_id"])
                print(manufacturer_aliases)

            product_client = ProductsExecutorClient()
            products = await product_client.get_all_by_manufacturer_id(manufacturer_id=manufacturer_id)
            print("### PRODUCTS ###")
            print(products)
            print("### END ###")
            for product in products:
                r = await product_client.modify(data={
                    "product_id": product["product_id"],
                    "manufacturer_id": origin_id})
            await manufacturer_client.remove_by_id(manufacturer_id=manufacturer_id)
        else:
            name = dublicate["name"]
            origin_id = dublicate["manufacturer_id"]
    print("removed " + str(counter) + " dublicates")

loop = asyncio.get_event_loop()
loop.run_until_complete(clean())
