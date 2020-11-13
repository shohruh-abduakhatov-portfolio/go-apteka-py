
import asyncio
import sys, os
sys.path.append(os.path.abspath(__file__ + "/../../"))
from modules.kinetic_core.AbstractExecutor import executor
from modules.kinetic_core.QueueListener import QueueListener
from TestExecutor import TestExecutor

@executor(TestExecutor)
class TestExecutorListener(QueueListener):
    async def parse(self, task):
        await TestExecutor(task).parse()

main_loop = asyncio.get_event_loop()
main_loop.create_task(TestExecutorListener().register_listener(main_loop))
main_loop.run_forever()