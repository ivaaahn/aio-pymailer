import asyncio
from functools import lru_cache

from core import MainConfig
from core.logger import LoggerFactory
from mailer.pymailer import PyMailer
from rabbitmq.mailer_worker import PyMailerWorker


@lru_cache
def get_config():
    return MainConfig()


@lru_cache
def get_logger_factory():
    return LoggerFactory(get_config().logger)


async def setup() -> PyMailerWorker:
    config = get_config()
    logger_factory = get_logger_factory()

    mailer = PyMailer(
        conf=config.mailer,
        logger=logger_factory.create("Mailer"),
    )

    return PyMailerWorker(
        mailer=mailer,
        conf=config.rmq,
        logger=logger_factory.create("RMQWorker"),
    )


async def main():
    log = get_logger_factory().create("ROOT")

    log.info("Setup environment...")
    py_mailer = await setup()

    log.info("py_mailer.run()")
    await py_mailer.run()


if __name__ == "__main__":
    asyncio.run(main())
