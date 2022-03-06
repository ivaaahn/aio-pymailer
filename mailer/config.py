from pydantic import BaseSettings


class MailerConf(BaseSettings):
    username: str
    sender: str
    token: str
    smtp_host: str = "smtp.yandex.ru"
    smtp_port: int = 465

    class Config:
        env_prefix = "mail_"
        env_file = ".env"
