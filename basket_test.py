 #!/usr/bin/python3.6
import os, sys

os.environ['VITA_CONFIG'] = '/var/www/config.py'
sys.path.append(os.path.abspath(__file__ + "/../"))
sys.path.append(os.path.abspath(__file__ + "/modules/pharmex/"))
print(sys.path)
import asyncio


async def main(loop):
    from modules.pharmex.basket.BasketExecutorClient_ph import BasketExecutorClient_ph
    bex = BasketExecutorClient_ph()
    #await bex.modify(data={"provision_ids": {}, "procurement_ids": {}, "basket_id": 2})
    # res = await bex.remove_procurement(data=)
    res = await bex.get_one(data={"basket_id": 8})
    res['procurement_ids'] = {}
    res = await bex.modify(data=res)
    print("qqqq")
    print(res)
    # from modules.kinetic_core.Connector import db
    #
    #
    # a = await db.list('select * from ph_users')
    # print(a)


loop = asyncio.get_event_loop()
result = loop.run_until_complete(main(loop))