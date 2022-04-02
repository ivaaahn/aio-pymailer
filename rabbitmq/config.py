from pydantic import BaseSettings


class RabbitMQConf(BaseSettings):
    host: str
    port: int
    user: str
    password: str
    queue_name: str
    reconnect_timeout: int = 5
    capacity: int = 10

    class Config:
        env_file = ".env"
        env_prefix = "rmq_"
