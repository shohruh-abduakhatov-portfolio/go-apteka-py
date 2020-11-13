# region import
import os  # NOQA: E402
import sys  # NOQA: E402
import uvloop  # NOQA: E402
uvloop.install()  # NOQA: E402
os.environ['VITA_CONFIG'] = '/var/www/config.py'  # NOQA: E402
sys.path.append(os.path.abspath(__file__ + "/../modules/business"))
from modules.kinetic_core.Connector import db
from authorization.CpUserExecutor import CpUserExecutor
from suppliers.SuppliersExportTemplateExecutor import SuppliersExportTemplateExecutor
from pricelists.PriceListExecutor import PriceList2Executor
from pricelists.PriceListRevisionExecutor import PriceListRevisionExecutor
from modules.kinetic_core.QueueListener import QueueListener
from modules.kinetic_core.AbstractExecutor import executor, attr
from modules.kinetic_core import Logger
from manufacturer.ManufacturerExecutor import ManufacturerExecutor
from dataclerk.DataClerkExecutor import DataClerkExecutor
import logging
import asyncio
from suppliers.aliases.AgentProductAliasesExecutor import AgentProductAliasesExecutor
from suppliers.aliases.AgentManufacturerAliasesExecutor import AgentManufacturerAliasesExecutor
from suppliers.SellerExecutor import SellerExecutor
from modules.kinetic_core.WebSocketConnector import WebSocketConnector
from dataclerk.task.DataClerkTaskExecutor import DataClerkTaskExecutor
from dataclerk.task.DataClerkTaskConnector import DataClerkTaskConnector
from dataclerk.task.DataClerkTaskClient import DataClerkTaskClient
from suppliers.aliases.AgentFullAliasesExecutor import AgentFullAliasesExecutor


# endregion

main_loop = asyncio.get_event_loop()

# Инициируем логгирование
Logger.init(logging.DEBUG)

# es_logger = logging.getLogger('elasticsearch')
# es_logger.setLevel(logging.WARNING)


# Регистрируем наш слушатель - он принимает сообщения из очереди rabbitMQ
@executor(DataClerkExecutor)
class DataClerkListener(QueueListener):

    async def parse(self, task):
        await DataClerkExecutor(task).parse()


# инициализируем коннектор websocket
webSocketConnector = WebSocketConnector(port=9004)
webSocketConnector.connect(main_loop, DataClerkTaskConnector)


@executor(DataClerkTaskExecutor)
class DataClerkTaskListener(QueueListener):

    async def parse(self, task):
        await DataClerkTaskExecutor(task, webSocketConnector).parse()


# Регистрируем наш слушатель - он принимает сообщения из очереди rabbitMQ
# @executor(SuppliersExportTemplateExecutor)
# class SuppliersExportTemplateListener(QueueListener):

#     async def parse(self, task):
#         await SuppliersExportTemplateExecutor(task).parse()


@executor(ManufacturerExecutor)
class ManufacturerListener(QueueListener):

    async def parse(self, task):
        await ManufacturerExecutor(task).parse()


@executor(AgentProductAliasesExecutor)
class AgentProductAliasesListener(QueueListener):

    async def parse(self, task):
        await AgentProductAliasesExecutor(task).parse()


@executor(AgentManufacturerAliasesExecutor)
class AgentManufacturerAliasesListener(QueueListener):

    async def parse(self, task):
        await AgentManufacturerAliasesExecutor(task).parse()


@executor(SellerExecutor)
class SellerListener(QueueListener):

    async def parse(self, task):
        await SellerExecutor(task).parse()


@executor(PriceListRevisionExecutor)
class PriceListRevisionListener(QueueListener):

    async def parse(self, task):
        await PriceListRevisionExecutor(task).parse()


# @executor(CpUserExecutor)
# class CpUserListener(QueueListener):

#     async def parse(self, task):
#         await CpUserExecutor(task).parse()


async def initialize():
    await db.query("select current_timestamp")
    # main_loop.create_task(CpUserListener().register_listener(main_loop))
    main_loop.create_task(
        PriceListRevisionListener().register_listener(main_loop))
    main_loop.create_task(SellerListener().register_listener(main_loop))
    main_loop.create_task(DataClerkTaskListener().register_listener(main_loop))
    # main_loop.create_task(
    #     SuppliersExportTemplateListener().register_listener(main_loop))
    main_loop.create_task(DataClerkListener().register_listener(main_loop))
    main_loop.create_task(ManufacturerListener().register_listener(main_loop))
    main_loop.create_task(
        AgentProductAliasesListener().register_listener(main_loop))
    main_loop.create_task(
        AgentManufacturerAliasesListener().register_listener(main_loop))


main_loop.create_task(initialize())
main_loop.run_forever()
