import asyncio
import sys
import os
os.environ['VITA_CONFIG'] = '/var/www/config.py'
# Add the ptdraft folder path to the sys.path list
sys.path.append('/Users/disturber/Documents/git/pharmex/')

sys.path.append(os.path.abspath(__file__ + "/../"))
sys.path.append(os.path.abspath(__file__ + "/../modules/vita/"))
import logging
from modules.kinetic_core import Logger
from elasticsearch_async import AsyncElasticsearch
from datetime import datetime
Logger.init(logging.DEBUG)
es = AsyncElasticsearch(hosts=['52.19.43.93'],
    http_auth=('vita', 'g6t7y7h98hyg67'),port=8080)

async def search():
    res = await es.search(index="productsexecutor-index", body={
            "query": {
                "constant_score" : {
                    "filter" : {
                        "terms" : { 
                            "alias.keyword": ["Фуразолидон таб 50мг №10"]
                        }
                    }
                }     
            },"from": 0, "size" : 10000
        })
    print("####")
    products = []
    for product in res["hits"]["hits"]:
        products.append(product["_source"])
    print(products)
    print("####")

loop = asyncio.get_event_loop()
loop.run_until_complete(search())
loop.close()
