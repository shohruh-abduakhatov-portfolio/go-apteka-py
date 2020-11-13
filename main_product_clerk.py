# region import
import sys  # NOQA: E402
import os  # NOQA: E402
os.environ['VITA_CONFIG'] = '/var/www/config.py'  # NOQA: E402


# Add the ptdraft folder path to the sys.path list
sys.path.append(os.path.abspath(__file__ + "/../"))  # NOQA: E402
sys.path.append(os.path.abspath(__file__ + "/../modules/vita"))  # NOQA: E402
sys.path.append(os.path.abspath(__file__ + "/../modules/business"))  # NOQA: E402

import asyncio
import logging

from dataclerk.DataClerkExecutor import DataClerkExecutor
from modules.kinetic_core import Logger
from modules.kinetic_core.AbstractExecutor import executor
from modules.kinetic_core.QueueListener import QueueListener

main_loop = asyncio.get_event_loop()

# Инициируем логгирование
Logger.init(logging.DEBUG)


# Регистрируем наш слушатель - он принимает сообщения из очереди rabbitMQ
@executor(DataClerkExecutor)
class DataClerkListener(QueueListener):

    async def parse(self, task):
        print("parse")
        await DataClerkExecutor(task).parse()


main_loop.create_task(DataClerkListener().register_listener(main_loop))
print("ready")
main_loop.run_forever()
