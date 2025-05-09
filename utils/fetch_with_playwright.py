import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from logger.logger import get_logger, save_log
from typing import Optional, Dict, Any, Union

load_dotenv()
PROXY = os.getenv('PROXIES')


def parse_proxy(proxy_url: str) -> Optional[Dict[str, Any]]:
    """ Parse proxy URL para Playwright """
    if not proxy_url:
        return None

    if proxy_url.startswith('http://'):
        proxy_url = proxy_url[7:]
    elif proxy_url.startswith('https://'):
        proxy_url = proxy_url[8:]

    if '@' in proxy_url:
        auth_part, server_part = proxy_url.split('@')
        username, password = auth_part.split(':')
        return {
            'server': server_part,
            'username': username,
            'password': password
        }
    else:
        return {
            'server': proxy_url
        }


async def fetch_with_playwright(url: str, headers: Optional[Dict[str, str]] = None, reference: str = 'default',
                                timeout: int = 30000) -> Optional[str]:
    """ Busca conteúdo da página usando Playwright, com fallback para proxy """
    logger = get_logger('playwright_fetcher', reference=reference)

    async def _fetch(proxy_server: Optional[str] = None) -> Optional[str]:
        async with async_playwright() as p:
            browser = None
            try:
                launch_kwargs: Dict[str, Union[bool, int, Dict[str, str]]] = {
                    'headless': True,
                    'timeout': timeout
                }

                if proxy_server:
                    proxy_config = parse_proxy(proxy_server)
                    if proxy_config:
                        launch_kwargs['proxy'] = {
                            'server': proxy_config['server'],
                            'username': proxy_config.get('username'),
                            'password': proxy_config.get('password')
                        }

                browser = await p.chromium.launch(**launch_kwargs)
                context = await browser.new_context()

                if headers:
                    await context.set_extra_http_headers(headers)

                page = await context.new_page()
                logger.info(f'🚀 Acessando URL: {url} {"(com proxy)" if proxy_server else "(sem proxy)"}')
                await save_log(
                    'INFO',
                    f'Iniciando requisição {"com proxy" if proxy_server else "sem proxy"} para {url}',
                    reference=reference
                )

                await page.goto(url, timeout=timeout)
                html = await page.content()

                logger.info('✅ Sucesso ao obter conteúdo')
                await save_log('INFO', 'Playwright obteve conteúdo com sucesso', reference=reference)

                return html

            except Exception as e:
                logger.warning(f"⚠️ Erro durante navegação: {str(e)}")
                await save_log('WARNING', f'Erro no Playwright: {str(e)}', reference=reference)
                return None

            finally:
                if browser:
                    await browser.close()

    try:
        result = await _fetch()
        if result:
            return result

        if PROXY:
            logger.info('🔁 Tentando novamente com proxy...')
            await save_log('INFO', 'Tentando requisição com proxy', reference=reference)
            return await _fetch(proxy_server=PROXY)

    except Exception as e:
        logger.error(f'❌ Falha crítica no Playwright: {str(e)}')
        await save_log('ERROR', f'Falha critica no Playwright: {str(e)}', reference=reference)

    return None