from authorization.CpUserExecutor import CpUserExecutor
from modules.kinetic_core.AbstractClient import AbstractClient, rpc
from modules.kinetic_core.AbstractExecutor import executor


@executor(CpUserExecutor)
class CpUserClient(AbstractClient):

    @rpc
    async def login(self, login, password):
        """
        Login into the system
        :param data: массив содержаний lat, lon и идентификатор
        :return: оптимизированный по расстоянию маршрут
        """
        pass

    @rpc
    async def logout(self, data):
        """
        Оптимизирует входящие данные
        :param data: массив содержаний lat, lon и идентификатор
        :return: оптимизированный по расстоянию маршрут
        """
        pass
