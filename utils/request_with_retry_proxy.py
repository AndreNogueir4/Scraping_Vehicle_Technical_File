import aiohttp
import asyncio
import time
import requests
import os
from lxml import html
from dotenv import load_dotenv
from logger.logger import get_logger, save_log

load_dotenv()
PROXIES = os.getenv('PROXIES', '').split(',')
REFERENCE = 'utils/request_with_retry_proxy'
logger = get_logger('request_with_retry_proxy', reference=REFERENCE)

def fichacompleta_proxy(url, headers, max_retries=5):
    for proxy in PROXIES:
        proxy_dict = {
            'http': proxy,
            'https': proxy
        }
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f'Tentando com proxy (tentativa {attempt}/{max_retries})')

                response = requests.get(url, headers=headers, proxies=proxy_dict)

                if response.status_code == 200:
                    tree = html.fromstring(response.text)
                    all_text = tree.xpath('//text')
                    if any('Digite o código:' in text for text in all_text):
                        logger.warning('CAPTCHA ainda presente com este proxy')
                        continue
                    return response.text
                else:
                    logger.warning(f'Proxy falhou com o status: {response.status_code}')
            except requests.RequestException as e:
                logger.warning(f'Erro com proxy: {e}')
            time.sleep(10)
    raise Exception('Todos os proxies falharam ou CAPTCHA persistiu')


async def icarros_proxy(url, headers, max_retries=5):
    for proxy in PROXIES:
        proxy_url = f'http://{proxy}'
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f'Tentando com proxy (tentativa {attempt}/{max_retries})')
                await save_log('INFO', f'Tentando com proxy (tentativa {attempt}/{max_retries})',
                               reference=REFERENCE)
                connector = aiohttp.TCPConnector(ssl=False)
                async with aiohttp.ClientSession(connector=connector) as session:
                    async with session.get(url, headers=headers, proxy=proxy_url) as response:

                        if response.status == 200:
                            return response
                        else:
                            logger.warning(f'Proxy falhou com o status: {response.status}')
            except aiohttp.ClientError as e:
                logger.warning(f'Erro com proxy: {e}')
            except asyncio.TimeoutError:
                logger.warning('Timeout com proxy')

            await asyncio.sleep(10)
    raise Exception('Todos os proxies falharam')
