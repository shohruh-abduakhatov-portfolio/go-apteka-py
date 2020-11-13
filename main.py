import asyncio
import logging

from authorization.UserClient import UserClient
from authorization.UserExecutor import UserExecutor
from modules.kinetic_core import Logger
from modules.kinetic_core.AbstractExecutor import client
from modules.kinetic_core.QueueListener import QueueListener

# главный луп приложения
main_loop = asyncio.get_event_loop()

# Инициируем логгирование
Logger.init(logging.DEBUG)


# Регистрируем наш слушатель - он принимает сообщения из очереди rabbitMQ
@client(UserClient)
class UserQueueListener(QueueListener):

    async def parse(self, task):
        await UserExecutor(task).parse()


main_loop.create_task(UserQueueListener().register_listener(main_loop))
main_loop.run_forever()
