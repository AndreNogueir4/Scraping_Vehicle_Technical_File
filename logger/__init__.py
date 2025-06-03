import logging
from typing import Optional, Dict
from colorlog import ColoredFormatter
from .handlers import MongoDBHandler
from .config import LogConfig

_logger_cache: Dict[str, logging.Logger] = {}

def get_logger(name: str = 'scraper', reference: Optional[str] = None) -> logging.Logger:
    cache_key = f'{name}:{reference}' if reference else name

    if cache_key in _logger_cache:
        return _logger_cache[cache_key]

    logger = logging.getLogger(cache_key)
    if logger.handlers:
        return logger

    setup_logger(logger, reference)
    _logger_cache[cache_key] = logger
    return logger

def setup_logger(logger: logging.Logger, reference: Optional[str] = None):
    logger.setLevel(LogConfig.LOG_LEVEL)
    logger.propagate = False

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    if LogConfig.USE_COLORED_LOGS:
        logger.addHandler(_create_console_handler())

    if LogConfig.USE_MONGO_HANDLER:
        logger.addHandler(_create_mongo_handler(reference))

def _create_console_handler() -> logging.Handler:
    handler = logging.StreamHandler()
    formatter = ColoredFormatter(
        '%(log_color)s%(asctime)s [%(levelname)s] %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    )
    handler.setFormatter(formatter)
    return handler

def _create_mongo_handler(reference: Optional[str] = None) -> logging.Handler:
    return MongoDBHandler(
        level=LogConfig.MONGO_LOG_LEVEL,
        reference=reference
    )