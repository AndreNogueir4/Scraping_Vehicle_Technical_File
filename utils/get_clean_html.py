import asyncio
import aiohttp
import os
from utils.url_validator import sanitize_url, is_valid_url
from logger.logger import get_logger, save_log
from utils.request_with_retry import request_with_proxy
from utils.fetch_with_playwright import fetch_with_playwright
from dotenv import load_dotenv

load_dotenv()
MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS'))
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

async def get_clean_html(url, headers, reference):
    logger = get_logger('get_clean_html', reference=reference)
    url = sanitize_url(url)
    logger.debug(f'🔍 Acessando URL sanitizada: {url}')

    if not is_valid_url(url):
        logger.error(f'❌ URL inválida: {url!r}')
        return None

    async with semaphore:
        async with aiohttp.ClientSession(headers=headers) as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        if 'Digite o código:' not in html_content:
                            return html_content
                        else:
                            raise Exception('Mensagem de erro encontrada no conteudo')
                    else:
                        raise Exception(f'Status ruim: {response.status}')
            except Exception as e:
                logger.warning(f'⚠️ Erro sem proxy: {e}')
                await save_log('WARNING', f'⚠️ Erro sem proxy: {e}', reference=reference)

        logger.info('Tentando buscar com proxy')
        html_content = await request_with_proxy(url, headers)
        if html_content and 'Digite o código:' not in html_content:
            return html_content

        logger.info('Tentando buscar com Playwright')
        html_content = await fetch_with_playwright(url, reference=reference)
        if html_content and 'Digite o código:' not in html_content:
            return html_content

        logger.error(f'❌ Falha mesmo usando proxy e Playwright para URL: {url!r}')
        await save_log('ERROR', f'❌ Falha mesmo usando proxy e Playwright para URL: {url!r}',
                       reference=reference)
        return None