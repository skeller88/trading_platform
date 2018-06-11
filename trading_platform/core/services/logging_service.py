import logging


class LoggingService:
    @staticmethod
    def set_logger(name=None, handler=logging.StreamHandler, level=logging.INFO):
        logger = logging.getLogger(name)
        logger.addHandler(handler)
        logger.setLevel(level)

    @staticmethod
    def get_logger(name=None):
        return logging.getLogger(name)