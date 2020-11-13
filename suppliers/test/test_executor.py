import asyncio
import logging

from modules.kinetic_core import Logger
from modules.kinetic_core.AbstractExecutor import executor
from modules.kinetic_core.QueueListener import QueueListener
# главный луп приложения
from suppliers.SuppliersExportTemplateExecutor import SuppliersExportTemplateExecutor

main_loop = asyncio.get_event_loop()

# Инициируем логгирование
Logger.init(logging.DEBUG)


# Регистрируем наш слушатель - он принимает сообщения из очереди rabbitMQ
@executor(SuppliersExportTemplateExecutor)
class SuppliersExportTemplateListener(QueueListener):

    async def parse(self, task):
        await SuppliersExportTemplateExecutor(task).parse()


main_loop.create_task(SuppliersExportTemplateListener().register_listener(main_loop))
main_loop.run_forever()
