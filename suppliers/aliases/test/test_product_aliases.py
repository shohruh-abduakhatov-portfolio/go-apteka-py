#!/usr/bin/python3.6
import sys  # NOQA: E402
import os  # NOQA: E402
# Add the ptdraft folder path to the sys.path list
sys.path.append('/Users/disturber/Documents/git/pharmex/')  # NOQA: E402
sys.path.append(os.path.abspath(__file__ + "/../modules/business/"))  # NOQA: E402

from datetime import datetime
import traceback
from suppliers.aliases.AgentManufacturerAliasesClient import AgentManufacturerAliasesClient
from suppliers.aliases.AgentProductAliasesClient import AgentProductAliasesClient
import asyncio


async def main():
    client = AgentProductAliasesClient()
    result = await client.delete(alias_id=17242)
    print(result)


async def test_():
    agent_manufacturers_client = AgentManufacturerAliasesClient()
    manufacturer_aliases_matches = await agent_manufacturers_client.matches(names=[u'hebei kaiwei pharmaceutical co. ltd, китай'])
    print("#####")
    print(manufacturer_aliases_matches)
    print("#####")


async def test_():
    agent_manufacturers_client = AgentManufacturerAliasesClient()
    manufacturer_aliases_matches = await agent_manufacturers_client.matches(names=[u'hebei kaiwei pharmaceutical co. ltd, китай'])
    print("#####")
    print(manufacturer_aliases_matches)
    print("#####")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
