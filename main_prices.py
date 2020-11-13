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


@executor(AgentFullAliasesExecutor)
class AgentFullAliasesListener(QueueListener):

    async def parse(self, task):
        await AgentFullAliasesExecutor(task).parse()


@executor(PriceList2Executor)
class PriceListListener(QueueListener):

    async def parse(self, task):
        await PriceList2Executor(task).parse()


async def initialize():
    await db.query("select current_timestamp")
    print("initialized")
    main_loop.create_task(
        AgentFullAliasesListener().register_listener(main_loop))

    main_loop.create_task(PriceListListener().register_listener(main_loop))


main_loop.create_task(initialize())
main_loop.run_forever()
