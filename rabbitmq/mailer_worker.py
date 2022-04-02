import asyncio
import json
import logging

from aio_pika import IncomingMessage

from mailer.pymailer import PyMailer
from mailer.schemas import MsgToSend
from .base import RabbitMQConsumer
from .config import RabbitMQConf


class PyMailerWorker(RabbitMQConsumer):
    class Meta:
        name = "PyMailerWorker"

    def __init__(self, mailer: PyMailer, conf: RabbitMQConf, logger: logging.Logger):
        super().__init__(conf, logger)
        self._mailer = mailer

    async def handler(self, msg: "IncomingMessage"):
        self.logger.debug("CAUGHT!")
        # await asyncio.sleep(15)
        self.logger.debug(str(self._extract_updates(msg)))
        await self._mailer.send_message(self._extract_updates(msg))
        self.logger.debug("DONE")

    @staticmethod
    def _extract_updates(msg: IncomingMessage) -> MsgToSend:
        return MsgToSend(**json.loads(msg.body.decode(encoding="utf-8")))
