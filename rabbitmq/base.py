import abc
import asyncio
import logging
from typing import Optional, TYPE_CHECKING

from aio_pika import connect

if TYPE_CHECKING:
    from rabbitmq.config import RabbitMQConf
    from aio_pika.connection import ConnectionType
    from aio_pika import Channel, Queue, IncomingMessage


class IRabbitMQConsumer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def handler(self, msg: "IncomingMessage"):
        raise NotImplementedError


class RabbitMQConsumer(IRabbitMQConsumer):
    class Meta:
        name = None

    def __init__(self, conf: "RabbitMQConf", logger: logging.Logger):
        self._conf = conf
        self._logger = logger
        self._name = self.Meta.name or self.__class__.__name__

        self._kill_event = asyncio.Event()
        self._stop_event = asyncio.Event()

        self._setup_stop_signals()

        self._connection: Optional["ConnectionType"] = None
        self._channel: Optional["Channel"] = None
        self._queue: Optional["Queue"] = None
        self._concurrent_workers: int = 0
        self._consume_tag: Optional[str] = None

        self._is_running: bool = False

    async def handler(self, msg: "IncomingMessage"):
        raise NotImplementedError

    def _setup_stop_signals(self):
        import signal
        import functools

        async def shutdown():
            self._kill_event.set()

        running_loop = asyncio.get_running_loop()
        handler = functools.partial(asyncio.create_task, shutdown())

        for sig in (signal.SIGINT,):
            running_loop.add_signal_handler(sig, handler)

    @property
    def conf(self) -> "RabbitMQConf":
        return self._conf

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    async def __connect(self):
        self._connection = await connect(
            host=self.conf.host,
            port=self.conf.port,
            login=self.conf.user,
            password=self.conf.password,
        )
        self._channel = await self._connection.channel()
        await self._channel.set_qos(prefetch_count=self.conf.capacity)
        self._queue = await self._channel.declare_queue(
            self.conf.queue_name, durable=True
        )

        self._is_running = True

    async def _connect(self) -> None:
        while True:
            try:
                await self.__connect()
                self._consume_tag = await self._queue.consume(self._worker)
                self.logger.info("RMQ WORKER CONNECTED")
                return
            except Exception as err:
                self.logger.error(
                    f"Cannot connect to rabbitmq ({self.conf.host}, {self.conf.port}): {err})"
                )
                await asyncio.sleep(self.conf.reconnect_timeout)

    async def _worker(self, msg: "IncomingMessage"):
        self.logger.debug(f">> {self._concurrent_workers + 1}")
        self._concurrent_workers += 1
        try:
            async with msg.process():
                await self.handler(msg)
        except Exception as e:
            self.logger.exception(e)
        finally:
            self._concurrent_workers -= 1
            self.logger.debug(f"<< {self._concurrent_workers}")
            if not self._is_running and not self._concurrent_workers:
                print("All workers is done. Ready to stop")
                self._stop_event.set()

    async def _disconnect(self):
        self.logger.info("_disconnect() was called")

        self._is_running = False

        if self._consume_tag:
            await self._queue.cancel(self._consume_tag)

        if self._concurrent_workers:
            print(f"Waiting for {self._concurrent_workers} workers...")
            await self._stop_event.wait()

        await self._connection.close()
        self.logger.info("_disconnected successfully")

    async def run(self):
        await self._connect()

        print(" [*] PyMailer waiting for messages. To exit press CTRL+C")
        await self._kill_event.wait()

        await self._disconnect()
        print("[x] PyMailer was gracefully shutdown")
