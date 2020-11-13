
import asyncio
import sys, os
sys.path.append(os.path.abspath(__file__ + "/../../"))
from TestClient import TestClient


async def test():
    test_client = TestClient()
    await test_client.heavy_operations()
    print("Finished")

main_loop = asyncio.get_event_loop()
main_loop.run_until_complete(test())