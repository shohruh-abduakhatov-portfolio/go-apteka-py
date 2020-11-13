import asyncio
import sys  # NOQA: E402
import os  # NOQA: E402
os.environ['VITA_CONFIG'] = '/var/www/config.py'  # NOQA: E402
sys.path.append(os.path.abspath(__file__ + "/../../../"))  # NOQA: E402
sys.path.append(os.path.abspath(__file__ + "/../../../modules/vita"))  # NOQA: E402
from suppliers.aliases.AgentManufacturerAliasesClient import AgentManufacturerAliasesClient
from modules.business.warehouse.ProductsExecutorClient import ProductsExecutorClient
from suppliers.aliases.AgentProductAliasesDB import AgentProductAliasesDB
from suppliers.aliases.AgentProductAliasesClient import AgentProductAliasesClient


async def test_list():
    db = AgentProductAliasesDB()
    aliases = await db.list()
    print(len(aliases))


async def validate_name():
    agent_products_client = AgentProductAliasesClient()
    print("before list")
    product_aliases = await agent_products_client.list_names()
    print("after list")

    product = "Жидкое мыло Полюшко Роза , 500 (ВОНДЕР КЛИИНИНГ ООО - )"
    print(product.lower())
    for alias, origin in product_aliases.items():
        if "полюшко" in alias:
            print(alias)
            print(origin)
    if str(product).lower() in product_aliases.keys():
        product = product_aliases[product.lower()]
        print("origin: " + product)
    products_client = ProductsExecutorClient()
    match_name = await products_client.get_one_name(data={"name": product})
    print(match_name)


async def validate_manufacturer():
    alias_manufacturer_client = AgentManufacturerAliasesClient()
    manufacturer_aliases_matches = await alias_manufacturer_client.matches(names=["grace pharma"])
    print(manufacturer_aliases_matches)


loop = asyncio.get_event_loop()
loop.run_until_complete(validate_name())
loop.close()
