import asyncio
import sys
import os
os.environ['VITA_CONFIG'] = '/var/www/config.py'
# Add the ptdraft folder path to the sys.path list
sys.path.append('/Users/disturber/Documents/git/pharmex/')

sys.path.append(os.path.abspath(__file__ + "/../"))
sys.path.append(os.path.abspath(__file__ + "/../modules/vita/"))
sys.path.append(os.path.abspath(__file__ + "/../modules/business/"))
import logging
from modules.kinetic_core import Logger
from elasticsearch_async import AsyncElasticsearch
from datetime import datetime
from agents.AgentExecutorClient import AgentExecutorClient
from supply.ProvisionExecutorClient import ProvisionExecutorClient
from warehouse.ProductsExecutorClient import ProductsExecutorClient
from warehouse.ProductsExecutor import ProductsExecutor
from transliterate import translit
Logger.init(logging.DEBUG)
es = AsyncElasticsearch(hosts=['52.19.43.93'],
                        http_auth=('vita', 'g6t7y7h98hyg67'), port=8080)


async def add():
    product_client = ProductsExecutorClient()
    products = await product_client.get_all()
    info = await es.info()
    print(info)

    for key, product in products.items():
        name = product["name"].lower()
        await product_client.modify(data={"product_id": product["product_id"], "name": product["name"]})
        print(product["product_id"])
        await es.delete("productsexecutor-index", doc_type="item", id=key)
        res = await es.index(index="productsexecutor-index",
                             doc_type='item', id=key, body=product)

    es.indices.refresh(index="productsexecutor-index")
    print("finished")


async def add_provisions():
    try:

        await es.indices.delete(index="provisionexecutor-index")
    except:
        pass
    provision_client = ProvisionExecutorClient()
    products = await provision_client.get_all_all()
    info = await es.info()
    print(info)

    for key, product in products.items():
        res = await es.index(index="provisionexecutor-index",
                             doc_type='item', id=key, body=product)

    es.indices.refresh(index="provisionexecutor-index")
    print("completed")


async def add_agents():
    agent_client = AgentExecutorClient()
    agents = await agent_client.get_all()

    for agent in agents:
        del agent["working_day_from"]
        del agent["working_day_until"]
        del agent["working_locations"]
        res = await es.index(index="agentexecutor-index",
                             doc_type='item', id=agent["agent_id"], body=agent)

    es.indices.refresh(index="agentexecutor-index")


async def delete():
    await es.indices.delete(index="music")


async def add2():
    await es.index(index="products2-index",
                   doc_type='item', id=1, body={"name": "цитрамон", "product_id": 1, "suggest": ["цитрамон"]})
    await es.index(index="products2-index",
                   doc_type='item', id=2, body={"name": "цинепар", "product_id": 2, "suggest": ["цинепар"]})


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

loop = asyncio.get_event_loop()
loop.create_task(add())
loop.run_forever()
