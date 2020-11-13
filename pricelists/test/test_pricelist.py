#!/usr/bin/python3.6
import sys
# Add the ptdraft folder path to the sys.path list
sys.path.append('/Users/disturber/Documents/git/pharmex/')
import asyncio

from pricelists.PriceListClient import PriceListClient


async def cycle():
    manufacturer = PriceListClient()
    result = await manufacturer.get_prices_for(ids=[5796])
    print(result)


loop = asyncio.get_event_loop()
loop.run_until_complete(cycle())
