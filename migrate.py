import asyncio
import logging
import sys
import os
import json
print(os.path.abspath(__file__ + "/../"))
sys.path.append(os.path.abspath(__file__ + "/../"))
sys.path.append(os.path.abspath(__file__ + "/../modules/business/"))
os.environ['VITA_CONFIG'] = '/var/www/config.py'  # NOQA: E402
from modules.kinetic_core.Connector import db
import asyncpg
import pprint
from modules.business.operations.TitleExecutorClient import TitleExecutorClient
from modules.business.operations.ManufacturerSynonymsExecutorClient import ManufacturerSynonymsExecutorClient
from modules.business.profiles.AgentExecutorClient import AgentExecutorClient
from modules.business.warehouse.manufacturer.ManufacturerClient import ManufacturerClient
refresh_title_data = False
refresh_manufacturer_synonyms = False

refresh_agents = False
refresh_manufacturer = True


async def migrate():
    pool = await asyncpg.create_pool(
        user="vita", password="sunny2411day",
        min_size=1, max_size=1,
        database="vita", host="vita.citioj9smjkf.eu-west-1.rds.amazonaws.com", port=5432)
    async with pool.acquire() as connection:
        async with connection.transaction():
            await connection.set_type_codec(
                'json',
                encoder=json.dumps,
                decoder=json.loads,
                schema='pg_catalog'
            )
            # shelves
            if refresh_title_data:
                r = await connection.fetch("select * from title_data")
                title_client = TitleExecutorClient()
                all = await title_client.paginate(limit=100000, offset=0)
                # for s in all["data"]:
                #     await title_client.remove(data={"product_id": s["product_id"]})

                for val in r:
                    val = dict(val)
                    val["name"] = json.loads(val["name"])
                    val["dosage_form"] = json.loads(val["dosage_form"])
                    val["marker"] = json.loads(val["marker"])
                    val["dosage_size_1"] = json.loads(val["dosage_size_1"])
                    val["dosage_size_2"] = json.loads(val["dosage_size_2"])
                    val["dosage_size_3"] = json.loads(val["dosage_size_3"])
                    val["dosage_size_unique"] = json.loads(
                        val["dosage_size_unique"])
                    val["per_dosage_size"] = json.loads(val["per_dosage_size"])
                    val["volume"] = json.loads(val["volume"])
                    val["quantity"] = json.loads(val["quantity"])
                    val["marker2"] = json.loads(val["marker2"])

                    await title_client.add(data=val)

            # racks
            if refresh_manufacturer_synonyms:
                r = await connection.fetch("select * from manufacturer_synonyms")
                manufacturer_client = ManufacturerSynonymsExecutorClient()
                all = await manufacturer_client.paginate(limit=100000, offset=0, term=None)
                # for s in all["data"]:
                #     await manufacturer_client.remove(data={"manufacturer_id": s["manufacturer_id"]})

                for val in r:
                    val = dict(val)
                    val["synonyms"] = json.loads(val["synonyms"])

                    await manufacturer_client.add(data=val)

            if refresh_agents:
                r = await connection.fetch("select * from pharmex_agents")
                agent_client = AgentExecutorClient()
                all = await agent_client.get_agents(limit=100000, offset=0)
                # for s in all["data"]:
                #     await agent_client.remove(data={"manufacturer_id": s["manufacturer_id"]})

                for val in r:
                    val = dict(val)

                    await agent_client.add_agent(data=val)

            if refresh_manufacturer:
                r = await connection.fetch("select * from manufacturers")
                manufacturer_client = ManufacturerClient()
                all = await manufacturer_client.paginate(limit=100000, offset=0)
                # for s in all["data"]:
                #     await manufacturer_client.remove(data={"manufacturer_id": s["manufacturer_id"]})

                for val in r:
                    val = dict(val)

                    await manufacturer_client.create(data=val)


loop = asyncio.get_event_loop()
loop.run_until_complete(migrate())
