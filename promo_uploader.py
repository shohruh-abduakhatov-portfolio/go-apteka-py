
import asyncio
import sys
import os
os.environ['VITA_CONFIG'] = '/var/www/config.py'
from modules.kinetic_core.Connector import db

import pandas as pd
# data = pd.read_excel("prices.xlsx")
data = pd.read_excel("prices.xlsx", sheet_name="Sheet3", header=None)


async def run():
    from collections import OrderedDict
    stopper = 0
    list = []
    cc = 0
    # tr = data.to_dict(orient='list', into=OrderedDict)
    for row in data.iterrows():
        promo = row[1][1]
        await db.query("insert into doctors_promocodes (promo) values ($1)", (promo,))
    print("finished")

loop = asyncio.get_event_loop()
loop.create_task(run())
loop.run_forever()
