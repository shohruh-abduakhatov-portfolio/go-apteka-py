 #!/usr/bin/python3.6
import os, sys

os.environ['VITA_CONFIG'] = '/var/www/config.py'
sys.path.append(os.path.abspath(__file__ + "/../"))
sys.path.append(os.path.abspath(__file__ + "/modules/pharmex/"))
print(sys.path)
import asyncio
from web.handlers.procurement.procurement_helper import data
from modules.pharmex.basket.BasketExecutorClient_ph import BasketExecutorClient_ph


async def main(loop):

    bex = BasketExecutorClient_ph()
    res = await bex.clear_basket(data={'basket_id': 8})
    print("qqqq")
    print(res)
    # from modules.kinetic_core.Connector import db
    #
    #
    # a = await db.list('select * from ph_users')
    # print(a)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(main(loop))