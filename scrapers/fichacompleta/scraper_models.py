import httpx
import asyncio
from lxml import html
from unidecode import unidecode
from logger.logger import get_logger
from fake_useragent import UserAgent
from utils.fichacompleta.get_proxy import get_proxy

REFERENCE = 'fichacompleta'
logger = get_logger('scraper_models', reference=REFERENCE)

def generate_headers_user_agent():
    ua = UserAgent()
    headers = {
        'Host': 'www.fichacompleta.com.br',
        'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Accept-Language': 'pt-BR',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
                  'q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Purpose': 'prefetch',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://www.fichacompleta.com.br/carros/marcas/',
        'Priority': 'u=4, i',
    }
    return headers

async def get_models(automaker):
    words_to_remove = ['Quem Somos', 'Contato', 'Política de Privacidade', 'Ver mais']
    url = f'https://www.fichacompleta.com.br/carros/{automaker}/'
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

                models = tree.xpath('//div/a/text()')
                models = [unidecode(model.lower().strip().replace(' ', '-'))
                          for model in models if model.strip() and model.strip() not in words_to_remove]
                return models

            elif response.status_code == 403:
                logger.warning('Status_code: 403 - Bloqueado. Tentando com proxies...')
                try:
                    response_text = await get_proxy(url, headers)
                    tree = html.fromstring(response_text)
                    models = tree.xpath('//div/a/text()')
                    models = [unidecode(model.lower().strip().replace(' ', '-'))
                              for model in models if model.strip() and model.strip() not in words_to_remove]
                    return models
                except Exception as proxy_e:
                    logger.warning(f'Falha ao tentar com proxies após 403: {proxy_e}')
                    return []

            else:
                logger.warning(f'Erro inicial {response.status_code}. Tentando com proxies...')
                try:
                    response_text = await get_proxy(url, headers)
                    tree = html.fromstring(response_text)
                    models = tree.xpath('//div/a/text()')
                    models = [unidecode(model.lower().strip().replace(' ', '-'))
                              for model in models if model.strip() and model.strip() not in words_to_remove]
                    return models
                except Exception as proxy_e:
                    logger.warning(f'Falha ao tentar com proxies após erro {response.status_code}: {proxy_e}')
                    return []

        except httpx.RequestError as e:
            logger.warning(f'Erro de requisição httpx na requisição inicial: {e}')
            logger.info('Tentando com proxies devido ao erro inicial...')
            try:
                response_text = await get_proxy(url, headers)
                tree = html.fromstring(response_text)
                models = tree.xpath('//div/a/text()')
                models = [unidecode(model.lower().strip().replace(' ', '-'))
                          for model in models if model.strip() and model.strip() not in words_to_remove]
                return models
            except Exception as proxy_e:
                logger.warning(f'Falha ao tentar com proxies após erro inicial: {proxy_e}')
                return []

        except asyncio.TimeoutError:
            logger.warning('Timeout na requisição inicial')
            logger.info('Tentando com proxies devido ao timeout inicial...')
            try:
                response_text = await get_proxy(url, headers)
                tree = html.fromstring(response_text)
                models = tree.xpath('//div/a/text()')
                models = [unidecode(model.lower().strip().replace(' ', '-'))
                          for model in models if model.strip() and model.strip() not in words_to_remove]
                return models
            except Exception as proxy_e:
                logger.warning(f'Falha ao tentar com proxies após timeout inicial: {proxy_e}')
                return []

        except Exception as e:
            logger.warning(f'Erro inesperado na função principal: {e}')
            return []