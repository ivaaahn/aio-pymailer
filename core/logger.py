import logging
from pydantic import BaseSettings


class LoggerConf(BaseSettings):
    base_level: str = "DEBUG"
    log_format: str = "%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
    stderr_logger: bool = True
    stderr_logger_level: str = "DEBUG"
    file_logger: bool = True
    file_logger_level: str = "WARNING"
    file_logger_filename: str = "logs.log"

    class Config:
        env_file = ".env"
        env_prefix = "log_"


class LoggerFactory:
    def __init__(self, conf: LoggerConf):
        self._conf = conf

    @property
    def conf(self) -> LoggerConf:
        return self._conf

    def _setup_logger(self, name: str) -> logging.Logger:
        logger = logging.getLogger(name)

        logger.setLevel(self.conf.base_level)

        if self.conf.file_logger:
            self._add_file_handler(logger)

        if self.conf.stderr_logger:
            self._add_stderr_handler(logger)

        return logger

    def create(self, name: str) -> logging.Logger:
        new_logger = self._setup_logger(name)
        return new_logger

    def _add_file_handler(self, logger: logging.Logger):
        file_handler = logging.FileHandler(self.conf.file_logger_filename)
        file_handler.setLevel(self.conf.file_logger_level)
        file_handler.setFormatter(logging.Formatter(self.conf.log_format))

        logger.addHandler(file_handler)

    def _add_stderr_handler(self, logger: logging.Logger):
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(self.conf.stderr_logger_level)
        stream_handler.setFormatter(logging.Formatter(self.conf.log_format))

        logger.addHandler(stream_handler)
