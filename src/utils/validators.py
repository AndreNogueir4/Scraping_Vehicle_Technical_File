from logger import get_logger

logger = get_logger('validators')

def validate_scraped_data(data, data_type: str, source: str) -> bool:
    if not data:
        logger.warning(f'⚠️ Dados inválidos para {data_type} ({source}) - lista vazia')
        return False

    if isinstance(data, (dict, list)) and len(data) == 0:
        logger.warning(f'⚠️ Dados inválidos para {data_type} ({source}) - contêiner vazio')
        return False

    return True