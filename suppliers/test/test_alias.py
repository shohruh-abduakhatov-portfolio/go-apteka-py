
import sys  # NOQA: E402
sys.path.append('/Users/disturber/Documents/git/pharmex/')  # NOQA: E402
sys.path.append('/mnt/c/Users/Anton/Documents/git/pharmex/')  # NOQA: E402
sys.path.append('/var/www/pharmex/')  # NOQA: E402
import os  # NOQA: E402
os.environ['VITA_CONFIG'] = '/var/www/config.py'  # NOQA: E402

from modules.kinetic_core.Connector import db
import asyncio
from manufacturer.ManufacturerClient import ManufacturerClient
from datetime import datetime
from modules.business.warehouse.ProductsExecutorClient import ProductsExecutorClient
from suppliers.aliases.AgentProductAliasesClient import AgentProductAliasesClient


async def test_alias():
    product = "Глицин таб 100мг №50"
    agent_products_client = AgentProductAliasesClient()
    product_aliases = await agent_products_client.list_names()
    if product.lower() in product_aliases:
        print("OK")
        return True
    print("not ok")
    return False


async def remove_alias():
    ids = await db.list("select * from suppliers_product_aliases where product_id not in (select product_id from products)")

    agent_products_client = AgentProductAliasesClient()
    for id_ in ids:
        print(id_["alias_id"])
        result = await agent_products_client.delete(alias_id=id_["alias_id"])
        print(result)
    return False


async def test_match():
    products_client = ProductsExecutorClient()
    product = "бромгексин сироп 40 мл"
    match_name = await products_client.get_one_name(data={"name": product})
    print(match_name)


async def test_manufacturer():
    manufacturer_client = ManufacturerClient()
    product = "healing grapes узбекистон"
    match_name = await manufacturer_client.get_by_name(name=product)
    print(match_name)


async def create_new_product():
    products_client = ProductsExecutorClient()
    await products_client.add({
        "name": "Детская присыпка 100 гр",
        "manufacturer": "healing grapes узбекистон"})

loop = asyncio.get_event_loop()
loop.run_until_complete(remove_alias())
