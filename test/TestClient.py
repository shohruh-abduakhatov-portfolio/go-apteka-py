from modules.kinetic_core.AbstractClient import AbstractClient, rpc
from modules.kinetic_core.AbstractExecutor import executor
from TestExecutor import TestExecutor


@executor(TestExecutor)
class TestClient(AbstractClient):

    @rpc
    async def heavy_operations(self):
        pass
