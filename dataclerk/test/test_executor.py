import asyncio
import logging

from dataclerk.DataClerkExecutor import DataClerkExecutor
from modules.kinetic_core import Logger
from modules.kinetic_core.AbstractExecutor import executor
from modules.kinetic_core.QueueListener import QueueListener

# главный луп приложения
main_loop = asyncio.get_event_loop()

# Инициируем логгирование
Logger.init(logging.DEBUG)


# Регистрируем наш слушатель - он принимает сообщения из очереди rabbitMQ
@executor(DataClerkExecutor)
class DataClerkListener(QueueListener):

    async def parse(self, task):
        await DataClerkExecutor(task).parse()

main_loop.create_task(DataClerkListener().register_listener(main_loop))
main_loop.run_forever()
