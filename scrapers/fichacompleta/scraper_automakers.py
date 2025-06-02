import httpx
import asyncio
from lxml import html
from unidecode import unidecode
from fake_useragent import UserAgent
from logger.logger import get_logger
from utils.fichacompleta.get_proxy import get_proxy


REFERENCE = 'fichacompleta'
logger = get_logger('scraper_automakers', reference=REFERENCE)

def generate_headers_user_agent():
    ua = UserAgent()
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;"
                  "q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "cache-control": "max-age=0",
        "priority": "u=0, i",
        "referer": "https://www.fichacompleta.com.br/carros/",
        "sec-ch-ua": '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": ua.random,
    }
    return headers

async def get_automakers():
    words_to_remove = ['Quem Somos', 'Contato', 'Política de Privacidade', 'Ver mais']
    url = 'https://www.fichacompleta.com.br/carros/marcas/'
    headers = generate_headers_user_agent()

    async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
        try:
            response = await client.get(url)
            response_text = response.text

            if response.status_code == 200:
                tree = html.fromstring(response_text)
                all_text = tree.xpath('//text()')
                if any('Digite o código:' in text for text in all_text):
                    logger.warning('CAPTCHA encontrado na resposta, tentando com proxies...')
                    try:
                        response_text = await get_proxy(url, headers)
                        tree = html.fromstring(response_text)
                    except Exception as proxy_e:
                        logger.warning(f'Falha ao tentar com proxies após CAPTCHA: {proxy_e}')
                        return []

                automakers = tree.xpath('//div/a/text()')
                automakers = [
                    unidecode(maker.lower().strip().replace(' ', '-'))
                    for maker in automakers if maker.strip() and maker.strip() not in words_to_remove
                ]
                return automakers

            elif response.status_code == 403:
                logger.warning('Status_code: 403 - Bloqueado. Tentando com proxies...')
                try:
                    response_text = await get_proxy(url, headers)
                    tree = html.fromstring(response_text)
                    automakers = tree.xpath('//div/a/text()')
                    automakers = [
                        unidecode(maker.lower().strip().replace(' ', '-'))
                        for maker in automakers if maker.strip() and maker.strip() not in words_to_remove
                    ]
                    return automakers
                except Exception as proxy_e:
                    logger.warning(f'Falha ao tentar com proxies após 403: {proxy_e}')
                    return []

            else:
                logger.warning(f'Erro inicial {response.status_code}. Tentando com proxies...')
                try:
                    response_text = await get_proxy(url, headers)
                    tree = html.fromstring(response_text)
                    automakers = tree.xpath('//div/a/text()')
                    automakers = [
                        unidecode(maker.lower().strip().replace(' ', '-'))
                        for maker in automakers if maker.strip() and maker.strip() not in words_to_remove
                    ]
                    return automakers
                except Exception as proxy_e:
                    logger.warning(f'Falha ao tentar com proxies após erro {response.status_code}: {proxy_e}')
                    return []

        except httpx.RequestError as e:
            logger.warning(f'Erro de requisição httpx na requisição inicial: {e}')
            logger.info('Tentando com proxies devido ao erro inicial...')
            try:
                response_text = await get_proxy(url, headers)
                tree = html.fromstring(response_text)
                automakers = tree.xpath('//div/a/text()')
                automakers = [
                    unidecode(maker.lower().strip().replace(' ', '-'))
                    for maker in automakers if maker.strip() and maker.strip() not in words_to_remove
                ]
                return automakers
            except Exception as proxy_e:
                logger.warning(f'Falha ao tentar com proxies após erro inicial: {proxy_e}')
                return []

        except asyncio.TimeoutError:
            logger.warning('Timeout na requisição inicial')
            logger.info('Tentando com proxies devido ao timeout inicial...')
            try:
                response_text = await get_proxy(url, headers)
                tree = html.fromstring(response_text)
                automakers = tree.xpath('//div/a/text()')
                automakers = [
                    unidecode(maker.lower().strip().replace(' ', '-'))
                    for maker in automakers if maker.strip() and maker.strip() not in words_to_remove
                ]
                return automakers
            except Exception as proxy_e:
                logger.warning(f'Falha ao tentar com proxies após timeout inicial: {proxy_e}')
                return []

        except Exception as e:
            logger.warning(f'Erro inesperado na função principal: {e}')
            return []