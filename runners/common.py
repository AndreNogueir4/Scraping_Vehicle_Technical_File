from logger.logger import get_logger

logger = get_logger('common', 'common')

async def validate_scraper_data(data, data_name, scraper_name):
    if not data:
        logger.error(f'⚠️ Dados vazios do scraper {scraper_name} - {data_name}')
        return False
    return True