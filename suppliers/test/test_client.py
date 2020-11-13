#!/usr/bin/python3.6
import sys
# Add the ptdraft folder path to the sys.path list
sys.path.append('/Users/disturber/Documents/git/pharmex/')
import asyncio
from datetime import datetime

from suppliers.SuppliersExportTemplateClient import SuppliersExportTemplateClient


async def add():
    picker = SuppliersExportTemplateClient()
    result = await picker.add(data={
        "name_column": 10,
        "json": {"t": "val", "d": datetime.now()}
    })
    print(result)


async def modify():
    picker = SuppliersExportTemplateClient()
    result = await picker.modify(data={
        "name_column": 2,
        "price_cash_column": 5,
        "price_wire100_column": 6,
        "price_wire100_percent": -1,
        "price_wire75_percent": 75,
        "price_wire50_percent": 50,
        "price_wire25_percent": 25,
        "manufacturer_column": 8,
        "expiry_column": 4,
        "row_offset": 19,
        "date_mask": '%d.%m.%y'
    }, filter=7)
    print(result)

async def list():
    template = SuppliersExportTemplateClient()
    print(await template.list())

loop = asyncio.get_event_loop()
loop.run_until_complete(modify())
