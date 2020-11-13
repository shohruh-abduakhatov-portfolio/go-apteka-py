import json
import asyncio
import sys  # NOQA: E402
import os  # NOQA: E402
os.environ['VITA_CONFIG'] = '/var/www/config.py'  # NOQA: E402
# Add the ptdraft folder path to the sys.path list
sys.path.append('/Users/disturber/Documents/git/pharmex/')  # NOQA: E402

sys.path.append(os.path.abspath(__file__ + "/../"))  # NOQA: E402
sys.path.append(os.path.abspath(__file__ + "/../modules/business/"))  # NOQA: E402
from modules.kinetic_core.Connector import db
from profiles.CustomerExecutorClient import CustomerExecutorClient
from warehouse.RackExecutorClient import RackExecutorClient
from modules.business.warehouse.ProductsExecutorClient import ProductsExecutorClient
from suppliers.aliases.AgentProductAliasesClient import AgentProductAliasesClient
from suppliers.aliases.AgentManufacturerAliasesClient import AgentManufacturerAliasesClient
from supply.ProvisionExecutorClient import ProvisionExecutorClient
from profiles.SupplierExecutorClient import SupplierExecutorClient
from warehouse.manufacturer.ManufacturerClient import ManufacturerClient

from pricelists.PriceListClient import PriceListClient

from datetime import datetime
from elasticsearch_async import AsyncElasticsearch
from modules.kinetic_core import Logger
import logging
from modules.kinetic_core.DateTimeEncoder import DateTimeEncoderCompact2

# Logger.init(logging.DEBUG)
es = AsyncElasticsearch(hosts=['52.19.152.166'],
                        http_auth=('vita', 'g6t7y7h98hyg67'), port=8080)


async def loadRacks():
    rack_client = RackExecutorClient()
    racks = await rack_client.db_get_all_by_warehouse(data={"warehouse_id": 1})
    for key, rack in racks.items():
        res = await es.index(index="rackexecutor-index",
                             doc_type='item', id=key, body=rack)

    es.indices.refresh(index="rackexecutor-index")


async def add():
    product_client = ProductsExecutorClient()
    products = await product_client.get_all()
    info = await es.info()
    print(info)

    for key, product in products.items():
        await product_client.modify(data={"product_id": product["product_id"], 'alternatives': {}, "association": {}})
        prd = await product_client.get_one(product_id=product["product_id"])
        print(key)
        try:
            res = await es.index(index="productsexecutor-index",
                                 doc_type='item', id=key, body=prd)
        except:
            print("error")
            print(key, prd)

    es.indices.refresh(index="productsexecutor-index")

    print("full")


async def add_manufacturers():
    await es.indices.delete(index="manufacturerexecutor-index")
    manufacturer_client = ManufacturerClient()
    products = await manufacturer_client.get_all()
    info = await es.info()
    print(info)

    for key, product in products.items():
        res = await es.index(index="manufacturerexecutor-index",
                             doc_type='item', id=key, body=product)

    es.indices.refresh(index="manufacturerexecutor-index")


async def add_customers():
    await es.indices.delete(index="customerexecutor-index")
    customer_client = CustomerExecutorClient()
    customers = await customer_client.paginate(limit=1000, offset=0)
    info = await es.info()
    print(info)

    for customer in customers["data"]:
        print(customer)
        res = await es.index(index="customerexecutor-index",
                             doc_type='item', id=customer["customer_id"], body=customer)

    es.indices.refresh(index="customerexecutor-index")


async def add_manufacturer_aliases():
    await es.indices.delete(index="agentmanufactureraliasesexecutor-index")
    alias_client = AgentManufacturerAliasesClient()
    products = await alias_client.get_all()
    info = await es.info()
    print(info)

    for key, product in products.items():
        res = await es.index(index="agentmanufactureraliasesexecutor-index",
                             doc_type='item', id=key, body=product)

    es.indices.refresh(index="agentmanufactureraliasesexecutor-index")


async def add_product_aliases():
    # await es.indices.delete(index="agentproductaliasesexecutor-index")
    alias_client = AgentProductAliasesClient()
    products = await alias_client.list(limit=1000000, offset=0)
    info = await es.info()
    print(info)

    for product in products["data"]:
        res = await es.index(index="agentproductaliasesexecutor-index",
                             doc_type='item', id=product["alias_id"], body=product)

    es.indices.refresh(index="agentproductaliasesexecutor-index")


async def add_supplier():
    try:
        await es.indices.delete(index="supplierexecutor-index")
    except:
        pass
    supplier_client = SupplierExecutorClient()
    suppliers = await supplier_client.get_all(data=None)
    import json
    for key, supplier in suppliers.items():
        res = await es.index(index="supplierexecutor-index",
                             doc_type='item', id=key, body=json.dumps(supplier, cls=DateTimeEncoderCompact2))

    es.indices.refresh(index="supplierexecutor-index")
    print(suppliers)


async def add_provisions():
    try:
        await es.indices.delete(index="provisionexecutor-index")
    except:
        pass
    provision_client = ProvisionExecutorClient()
    provisions = await provision_client.get_all(data=None)
    import json
    for key, provision in provisions.items():
        res = await es.index(index="provisionexecutor-index",
                             doc_type='item', id=key, body=json.dumps(provision, cls=DateTimeEncoderCompact2))

    es.indices.refresh(index="provisionexecutor-index")


async def delete():
    await es.indices.delete(index="stockexecutor-index")


async def add2():
    await es.index(index="products2-index",
                   doc_type='item', id=1, body={"name": "цитрамон", "product_id": 1, "suggest": ["цитрамон"]})
    await es.index(index="products2-index",
                   doc_type='item', id=2, body={"name": "цинепар", "product_id": 2, "suggest": ["цинепар"]})


async def add_p2():
    print('add p2 was called')
    try:
        await es.indices.delete(index="pricelist2executor-index")
    except:
        pass
    pricelist_client = PriceListClient()
    prices = await pricelist_client.get_all_db()
    import json
    print('got to prices')
    for price in prices:
        print(price)
        res = await es.index(index="pricelist2executor-index",
                             doc_type='item', id=price["price_list_id"], body=json.dumps(price, cls=DateTimeEncoderCompact2))

    es.indices.refresh(index="pricelist2executor-index")


async def print_info():
    info = await es.info()
    print(info)
    res = await es.search(index="agentexecutor-index", body={
        "query": {
            "prefix": {
                "company_name": "Омега"
            }
        },
    })
    print(res)

    res = await es.search(index="agentexecutor-index,productsexecutor-index", body={
        "query": {
            "multi_match": {
                "query": "Омега",
                "type": "phrase_prefix",
                "fields": ["company_name", "name"]
            }
        },
    }
    )
    print(res['hits'])

    # res = await es.search(index="products2-index", body={
    #         "suggest": {
    #         "suggest": {
    #                 "prefix":"цине",
    #                 "completion" : {
    #                     "field" : "suggest"
    #                 }
    #         }
    #         }
    #     })
    # print("Got %d Hits:" % res['hits']['total'])
    # for hit in res['hits']['hits']:
    #     print(hit["_source"])


async def fix_products_with_wrong_manufacturers():
    agent_manufacturers_client = AgentManufacturerAliasesClient()
    products = await db.list("select *, current_timestamp from products where manufacturer_id=0")
    manufacturers = set()
    for product in products:
        manufacturers.add(product["manufacturer"].lower())

    manufacturer_client = ManufacturerClient()
    manufacturers_l = list(manufacturers)
    print(manufacturers_l)
    manufacturer_aliases_matches = await agent_manufacturers_client.matches(names=manufacturers_l)
    print(manufacturer_aliases_matches)
    product_client = ProductsExecutorClient()
    others = list()
    for product in products:
        manufacturer = product["manufacturer"]
        if manufacturer.lower() in manufacturer_aliases_matches:
            new_mnf = manufacturer_aliases_matches[manufacturer.lower()]
            data = {
                "product_id": product["product_id"],
                "manufacturer_id": new_mnf["manufacturer_id"],
                "manufacturer": new_mnf["origin"]}
            print(data)
            await product_client.modify(data=data)
        else:
            others.append(product)

    manufacturer_matches = await manufacturer_client.matches(names=manufacturers_l)
    for product in others:
        manufacturer = product["manufacturer"]
        if manufacturer.lower() in manufacturer_matches:
            new_mnf = manufacturer_matches[manufacturer.lower()]
            data = {
                "product_id": product["product_id"],
                "manufacturer_id": new_mnf["manufacturer_id"],
                "manufacturer": new_mnf["name"]}
            print(data)
            await product_client.modify(data=data)

    print("finish")


async def move_move():
    manufacturer_id = 19465
    manufacturer_client = ManufacturerClient()

    new_manufacturer_id = 18284
    print("## NEW ##")
    manufacturer = await manufacturer_client.get_by_id(mid=new_manufacturer_id)
    print(manufacturer)
    print("## END ##")
    alias_client = AgentManufacturerAliasesClient()
    aliases = await alias_client.list_by_manufacturer_id(manufacturer_id=manufacturer_id)
    print("### ALIASES ###")
    print(aliases)
    print("### END ###")

    for alias in aliases:
        manufacturer_aliases = await alias_client.modify(data={
            "manufacturer_id": manufacturer["manufacturer_id"],
            "origin": manufacturer["name"]}, filter=alias["alias_id"])
        print(manufacturer_aliases)

    product_client = ProductsExecutorClient()
    products = await product_client.get_all_by_manufacturer_id(manufacturer_id=manufacturer_id)
    print("### PRODUCTS ###")
    print(products)
    print("### END ###")
    for product in products:
        r = await product_client.modify(data={
            "product_id": product["product_id"],
            "manufacturer_id": manufacturer["manufacturer_id"],
            "manufacturer": manufacturer["name"]})
    # manufacturer_aliases = await m_client.modify(data={
    #     "manufacturer_id":18597,
    #     "origin": "world medicine"}, filter=3644)

    r = await manufacturer_client.remove_by_id(manufacturer_id=manufacturer_id)
    print({"status": "success"})


async def test_elastic_multiple():
    q = {
        "query": {
            "bool": {
                "must": {
                    "bool": {
                        "should": [
                            {"match": {"title": "Галавит супп. рект. 100мг №10"}},
                        ],
                        "must": {"match": {"manufacturer_id": "19360"}}
                    }
                }
            }
        }
    }
    res = await es.search(index="agentexecutor-index,productsexecutor-index", body=q)
    print("---")
    print(res['hits']["hits"])

loop = asyncio.get_event_loop()
# loop.run_until_complete(loadRacks())
loop.create_task(add())
loop.run_forever()
