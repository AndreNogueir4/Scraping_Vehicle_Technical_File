import aiohttp
from logger.logger import get_logger, save_log
from utils.request_with_retry import request_with_proxy
from utils.fetch_with_playwright import fetch_with_playwright


async def get_clean_html(url, headers, reference):
    logger = get_logger('get_clean_html', reference=reference)

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
    html_content = await fetch_with_playwright(url, headers=headers, reference=reference)
    if html_content and 'Digite o código:' not in html_content:
        return html_content

    logger.error('❌ Falha mesmo usando proxy e Playwright.')
    await save_log('ERROR', '❌ Falha mesmo usando proxy e Playwright.', reference=reference)
    return None