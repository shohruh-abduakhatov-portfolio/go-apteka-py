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
from modules.kinetic_core.Connector import db
from transliterate import translit
Logger.init(logging.DEBUG)
es = AsyncElasticsearch(hosts=['52.19.43.93'],
                        http_auth=('vita', 'g6t7y7h98hyg67'), port=8080)


async def clean():
    wrong = await db.list("select price_list_id, current_timestamp from pharmex_pricelists where key in (select key from pharmex_pricelist_revision where deactivated_at is not null)")

    for data in wrong:
        price_list_id = int(data["price_list_id"])
        print(price_list_id)
        await db.query("delete from pharmex_pricelists where price_list_id = $1", (int(data["price_list_id"]),))
        try:
            await es.delete(index='pricelist2executor-index', doc_type='item',
                            id=price_list_id)
        except:
            pass
        print("deleted " + str(price_list_id))

    es.indices.refresh(index="pricelist2executor-index")
    print("finished")

loop = asyncio.get_event_loop()
loop.create_task(clean())
loop.run_forever()
