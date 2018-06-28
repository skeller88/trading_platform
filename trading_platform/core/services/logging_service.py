import logging
import sys


class LoggingService:
    @staticmethod
    def set_logger(name=None, handler=None, level=logging.INFO) -> logging.Logger:
        logger = logging.getLogger(name)
        handler = logging.StreamHandler(sys.stdout) if handler is None else handler
        logger.addHandler(handler)
        logger.setLevel(level)
        return logger

    @staticmethod
    def get_default_formatter() -> logging.Formatter:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        return formatter

    @staticmethod
    def get_logger(name=None):
        return logging.getLogger(name)