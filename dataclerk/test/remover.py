#!/usr/bin/python3.6

import asyncio
import sys
# Add the ptdraft folder path to the sys.path list
sys.path.append('/Users/disturber/Documents/git/pharmex/')

import traceback
from datetime import datetime

from dataclerk.task.DataClerkTaskClient import DataClerkTaskClient

async def main(loop):
    client = DataClerkTaskClient()
    result = await client.delete(task_id="1548058204.128693")
    print(result)

loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))

