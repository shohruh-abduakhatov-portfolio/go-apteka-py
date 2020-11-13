#!/usr/bin/python3.6
import sys
# Add the ptdraft folder path to the sys.path list
sys.path.append('/Users/disturber/Documents/git/pharmex/')
sys.path.append('/Users/disturber/Documents/git/pharmex/modules/vita/')
import asyncio
from profiles.AgentUserExecutorClient import AgentUserExecutorClient


async def add():
    picker = AgentUserExecutorClient()
    result = await picker.modify(user_id=28, data={"telegram_id": 446563947})
    print(result)


loop = asyncio.get_event_loop()
loop.run_until_complete(add())
