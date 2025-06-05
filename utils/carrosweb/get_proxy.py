import httpx
import os
import asyncio
from lxml import html
from dotenv import load_dotenv
from logger.logger import get_logger

REFERENCE = 'carrosweb'
logger = get_logger('get_proxy', reference=REFERENCE)

load_dotenv()
PROXIES = [p.strip() for p in os.getenv('PROXIES', '').split(',') if p.strip()]

async def get_proxy(url, headers, params=None, max_retries=5):
    if not PROXIES:
        logger.warning('Nenhum proxy configurado para tentar')
        raise Exception('Tentativa de usar proxies falhou: nenhum proxy fornecido')

    for proxy in PROXIES:
        if not proxy.startswith('http://') and not proxy.startswith('https://'):
            logger.warning(f'Formato de proxy inválidos: {proxy}. Deve começar com http:// ou https://')
            continue

        logger.info(f'Tentando proxy: {proxy}')
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f'Tentativa {attempt}/{max_retries} com proxy {proxy}')
                proxies = {
                    'http://': proxy,
                    'https://': proxy
                }

                async with httpx.AsyncClient(headers=headers, proxies=proxies, timeout=30.0) as proxy_client:
                    response = await proxy_client.get(url, params)
                    response_text = response.text

                    if response.status_code == 200:
                        tree = html.fromstring(response_text)
                        all_text = tree.xpath('//text()')
                        if any('Ocorreu um erro.' in text for text in all_text):
                            logger.warning(f'CAPTCHA presente com proxy: {proxy}')
                        return response_text
                    else:
                        logger.warning(f'Proxy {proxy} falhou com status: {response.status_code}')

            except httpx.RequestError as e:
                logger.warning(f'Erro de requisição httpx com proxy: {proxy} (tentativa {attempt}): {e}')
            except asyncio.TimeoutError:
                logger.warning(f'Timeout com proxy: {proxy} (tentativa {attempt})')
            except Exception as e:
                logger.warning(f'Erro inesperado com proxy: {proxy} (tentativa {attempt}): {e}')

            if attempt < max_retries:
                await asyncio.sleep(5)

        logger.warning(f'Falha em todas as tentativas com proxy: {proxy}')
    raise Exception('Todos os proxies falharam, e requisição não foi obtida após todas as tentativas')