#!/usr/bin/python3.6

import asyncio
import sys
# Add the ptdraft folder path to the sys.path list
sys.path.append('/mnt/c/Users/Anton/Documents/git/pharmex/modules/vita/')
from profiles.AgentExecutorClient import AgentExecutorClient

agent_client = AgentExecutorClient()


async def modify():
    result = await agent_client.modify_agent(agent_id=27, data={
        "company_name": "Кто-то",
        "inn": 123445,
        "mfo": 54321,
        "buyer": 1,
        "is_manufacturer": 1,
        "supplier": 1,
        "address": "Tashkent City",
        "working_locations": [6, 7, 8, 9]
    })
    print(result)

loop = asyncio.get_event_loop()
loop.run_until_complete(modify())
