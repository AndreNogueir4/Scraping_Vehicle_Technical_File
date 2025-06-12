import httpx
import os
import asyncio
from lxml import html
from dotenv import load_dotenv
from src.logger.logger import get_logger

REFERENCE = 'fichacompleta'
logger = get_logger('get_proxy', reference=REFERENCE)

load_dotenv()
PROXIES = [p.strip() for p in os.getenv('PROXIES', '').split(',') if p.strip()]

async def get_proxy(url, headers, max_retries=5):
    if not PROXIES:
        logger.warning('No proxy configured to try')
        raise Exception('Attempt to use proxies failed: No proxy provided')

    for proxy in PROXIES:
        if not proxy.startswith('http://') and not proxy.startswith('https://'):
            logger.warning(f'Invalid proxy format: {proxy}. Must start with http:// or https://')
            continue

        logger.info(f'Trying proxy: {proxy}')
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f'Attempt {attempt}/{max_retries} with proxy {proxy}')
                proxies = {
                    'http://': proxy,
                    'https://': proxy
                }

                async with httpx.AsyncClient(headers=headers, proxies=proxies, timeout=30.0) as proxy_client:
                    response = await proxy_client.get(url)
                    response_text = response.text

                    if response.status_code == 200:
                        tree = html.fromstring(response_text)
                        all_text = tree.xpath('//text')
                        if any('Digite o código:' in text for text in all_text):
                            logger.warning(f'CAPTCHA present with proxy: {proxy}')
                        return response_text
                    else:
                        logger.warning(f'Proxy {proxy} failed with status: {response.status_code}')

            except httpx.RequestError as e:
                logger.warning(f'https request error with proxy: {proxy} (attempt {attempt}): {e}')
            except asyncio.TimeoutError:
                logger.warning(f'Timeout with proxy: {proxy} (attempt {attempt})')
            except Exception as e:
                logger.warning(f'Unexpected error with proxy: {proxy} (attempt {attempt}): {e}')

            if attempt < max_retries:
                await asyncio.sleep(5)

        logger.warning(f'All attempts with proxy failed: {proxy}')
    raise Exception('All proxies failed, and request was not successful after all attempts')