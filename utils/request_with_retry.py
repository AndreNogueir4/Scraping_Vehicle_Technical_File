import aiohttp
import os
from dotenv import load_dotenv
from logger.logger import get_logger

load_dotenv()
logger = get_logger('request_with_retry')

PROXIES = os.getenv('PROXIES', '').split(',')

async def request_with_proxy(url, params=None, headers=None):
    """ Faz uma request usando proxies """
    for proxy in PROXIES:
        try:
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
                async with session.get(url, params=params, proxy=proxy if proxy else None, timeout=100) as response:
                    if response.status == 200:
                        logger.info(f'✅ Request com proxy {proxy or "sem proxy"} funcionou.')
                        return await response.text()
                    else:
                        logger.warning(f'⚠️ Status ruim {response.status} com proxy {proxy}')
        except Exception as e:
            logger.warning(f'⚠️ Erro tentando proxy {proxy}: {e}')

    logger.error('❌ Todas as tentativas com proxy falharam.')
    return None
