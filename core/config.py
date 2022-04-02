from pydantic import BaseSettings

from core.logger import LoggerConf
from mailer.config import MailerConf
from rabbitmq.config import RabbitMQConf


class MainConfig(BaseSettings):
    mailer: MailerConf = MailerConf()
    rmq: RabbitMQConf = RabbitMQConf()
    logger: LoggerConf = LoggerConf()

    class Config:
        env_file = ".env"
