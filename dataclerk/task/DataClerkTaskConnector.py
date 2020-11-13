import logging
from abc import ABC

from modules.kinetic_core.AbstractWebSocketProtocol import AbstractWebSocketProtocol


class DataClerkTaskConnector(AbstractWebSocketProtocol, ABC):

    def __init__(self):
        super().__init__()

    async def onPacket(self, text):
        logging.info(text)
