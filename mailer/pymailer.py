import logging

from .config import MailerConf
from .schemas import MsgToSend

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig


class PyMailer:
    def __init__(self, conf: MailerConf, logger: logging.Logger):
        self._conf = conf
        self._logger = logger

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @property
    def conf(self) -> MailerConf:
        return self._conf

    def _make_connection_config(self) -> ConnectionConfig:
        return ConnectionConfig(
            MAIL_USERNAME=self.conf.username,
            MAIL_PASSWORD=self.conf.token,
            MAIL_FROM=self.conf.sender,
            MAIL_PORT=self.conf.smtp_port,
            MAIL_SERVER=self.conf.smtp_host,
            TEMPLATE_FOLDER="mailer/templates",
        )

    async def send_message(self, msg: MsgToSend):
        message = MessageSchema(
            subject=msg.subject,
            recipients=msg.recipients,
            body=msg.regular_body if not msg.formatted_body else None,
            subtype=msg.subtype,
            template_body=msg.formatted_body.dict() if msg.formatted_body else None,
        )

        self.logger.info(str(msg))

        fm = FastMail(self._make_connection_config())
        await fm.send_message(message, template_name="email.html")
