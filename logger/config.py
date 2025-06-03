import logging
import os

class LogConfig:
    LOG_LEVEL = logging.DEBUG
    MONGO_LOG_LEVEL = logging.INFO

    USE_COLORED_LOGS = True
    USE_MONGO_HANDLER = True

    MONGO_LOG_COLLECTION = os.getenv('MONGO_LOG_COLLECTION', 'logs')