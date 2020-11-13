import asyncio
import sys
sys.path.append('/Users/disturber/Documents/git/pharmex/')

from suppliers.SuppliersExportTemplateClient import SuppliersExportTemplateClient


async def main():
    client = SuppliersExportTemplateClient()
    tpl = await client.get_one(key=7)
    print(tpl)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())