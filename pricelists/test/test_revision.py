#!/usr/bin/python3.6
import sys
# Add the ptdraft folder path to the sys.path list
sys.path.append('/Users/disturber/Documents/git/pharmex/')
import asyncio

from pricelist.PriceListRevisionClient import PriceListRevisionClient


async def cycle():
    revision_client = PriceListRevisionClient()
    revision = await revision_client.get_one(key="1541748913.068387")
    print("before")
    print(revision)
    result = await revision_client.is_manual(key="1541748913.068387", manual=True)
    print(result)
    revision = await revision_client.get_one(key="1541748913.068387")
    print("after")
    print(revision)


loop = asyncio.get_event_loop()
loop.run_until_complete(cycle())
