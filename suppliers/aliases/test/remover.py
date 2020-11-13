import asyncio  # NOQA: E402
import os  # NOQA: E402
import sys  # NOQA: E402
os.environ['VITA_CONFIG'] = '/var/www/config.py'  # NOQA: E402

sys.path.append(os.path.abspath(__file__ + "/../../../../"))  # NOQA: E402
sys.path.append(os.path.abspath(__file__ + "/../../../../modules/business/"))  # NOQA: E402
print(os.path.abspath(__file__ + "/../../../../"))  # NOQA: E402

from suppliers.aliases.AgentFullAliasesClient import AgentFullAliasesClient
from modules.kinetic_core.Connector import db


async def remove():
    alias_client = AgentFullAliasesClient()
    aliases = await db.list("select * from suppliers_full_aliases")
    for alias in aliases:
        await alias_client.delete(alias_id=alias["alias_id"])
    print("finished")
    pass

loop = asyncio.get_event_loop()
loop.run_until_complete(remove())
