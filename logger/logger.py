import logging
import sys

import colorlog
import datetime
import asyncio
from db.mongo import insert_log

_logger_cache = {}

async def save_log(level, message, reference=None):
    """ Salva o log no MongoDB com nível, mensagem, timestamp e referência (site de origem) """
    log_entry = {
        'level': level,
        'message': message,
        'timestamp': datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    }
    await insert_log(log_entry, reference=reference)

class MongoDBHandler(logging.Handler):
    """ Handler personalizado que envia logs para o MongoDB """
    def __init__(self, reference=None):
        super().__init__()
        self.reference = reference

    def emit(self, record):
        message = self.format(record)
        asyncio.create_task(save_log(record.levelname, message, self.reference))

def get_logger(name: str = 'scraper', reference: str = None):
    """
    Retorna um logger com saída colorida no terminal e envio de logs para o MongoDB
    O campo 'reference' indica de qual site o log se origina
    """
    cache_key = f'{name}:{reference}'

    if cache_key in _logger_cache:
        return _logger_cache[cache_key]

    logger = logging.getLogger(cache_key)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    is_test = any('pytest' in arg for arg in sys.argv)

    if is_test:
        log_colors = {
            'DEBUG': 'bold_purple',
            'INFO': 'bold_purple',
            'WARNING': 'bold_purple',
            'ERROR': 'bold_purple',
            'CRITICAL': 'bold_purple',
        }
    else:
        log_colors = {
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }

    stream_handler = colorlog.StreamHandler()
    stream_handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s [%(levelname)s] - %(message)s',
        log_colors=log_colors
    ))
    logger.addHandler(stream_handler)

    mongo_handler = MongoDBHandler(reference=reference)
    mongo_handler.setLevel(logging.DEBUG)
    logger.addHandler(mongo_handler)

    _logger_cache[cache_key] = logger
    return logger