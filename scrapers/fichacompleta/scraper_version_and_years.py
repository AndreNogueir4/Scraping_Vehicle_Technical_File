import httpx
import asyncio
import re
from lxml import html
from fake_useragent import UserAgent
from logger.logger import get_logger
from utils.fichacompleta.get_proxy import get_proxy

REFERENCE = 'fichacompleta'
logger = get_logger('scraper_version_and_years', reference=REFERENCE)

def generate_headers_user_agent(automaker):
    ua = UserAgent()
    reference = f'https://www.fichacompleta.com.br/carros/{automaker}/'

    headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive',
        'Referer': reference,
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'DNT': '1',
        'Sec-GPC': '1',
        'Priority': 'u=0, i',
    }

    return headers

async def get_version_years(automaker, model):
    words_to_remove = ['Quem Somos', 'Contato', 'Política de Privacidade', 'Ver mais']
    versions = {}
    years = []

    model = model.replace('.', '-').replace(':', '-').replace(' ', '-')
    if model.endswith('-'):
        model = model[:-1]

    url = f'https://www.fichacompleta.com.br/carros/{automaker}/{model}/'
    headers = generate_headers_user_agent(automaker)

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

                for element in tree.xpath('//div/a[normalize-space(text())]'):
                    text = element.text.strip()
                    href = element.get('href', '').strip()
                    if href and not any(word in text for word in words_to_remove):
                        versions[text] = href
                        year_math = re.match(r'^\d{4}', text.strip())
                        if year_math:
                            year = year_math.group(0)
                            if year not in ['Carregando', 'Carregando...']:
                                years.append(year)
                return versions, years

            elif response.status_code == 403:
                logger.warning('Status_code: 403 - Bloqueado. Tentando com proxies...')
                try:
                    response_text = await get_proxy(url, headers)
                    tree = html.fromstring(response_text)
                    for element in tree.xpath('//div/a[normalize-space(text())]'):
                        text = element.text.strip()
                        href = element.get('href', '').strip()
                        if href and not any(word in text for word in words_to_remove):
                            versions[text] = href
                            year_math = re.match(r'^\d{4}', text.strip())
                            if year_math:
                                year = year_math.group(0)
                                if year not in ['Carregando', 'Carregando...']:
                                    years.append(year)
                    return versions, years
                except Exception as proxy_e:
                    logger.warning(f'Falha ao tentar com proxies após 403: {proxy_e}')
                    return []

            else:
                logger.warning(f'Erro inicial {response.status_code}. Tentando com proxies...')
                try:
                    response_text = await get_proxy(url, headers)
                    tree = html.fromstring(response_text)
                    for element in tree.xpath('//div/a[normalize-space(text())]'):
                        text = element.text.strip()
                        href = element.get('href', '').strip()
                        if href and not any(word in text for word in words_to_remove):
                            versions[text] = href
                            year_math = re.match(r'^\d{4}', text.strip())
                            if year_math:
                                year = year_math.group(0)
                                if year not in ['Carregando', 'Carregando...']:
                                    years.append(year)
                    return versions, years
                except Exception as proxy_e:
                    logger.warning(f'Falha ao tentar com proxies após erro {response.status_code}: {proxy_e}')
                    return []

        except httpx.RequestError as e:
            logger.warning(f'Erro de requisição httpx na requisição inicial: {e}')
            logger.info('Tentando com proxies devido ao erro inicial...')
            try:
                response_text = await get_proxy(url, headers)
                tree = html.fromstring(response_text)
                for element in tree.xpath('//div/a[normalize-space(text())]'):
                    text = element.text.strip()
                    href = element.get('href', '').strip()
                    if href and not any(word in text for word in words_to_remove):
                        versions[text] = href
                        year_math = re.match(r'^\d{4}', text.strip())
                        if year_math:
                            year = year_math.group(0)
                            if year not in ['Carregando', 'Carregando...']:
                                years.append(year)
                return versions, years
            except Exception as proxy_e:
                logger.warning(f'Falha ao tentar com proxies após erro inicial: {proxy_e}')
                return []

        except asyncio.TimeoutError:
            logger.warning('Timeout na requisição inicial')
            logger.info('Tentando com proxies devido ao timeout inicial...')
            try:
                response_text = await get_proxy(url, headers)
                tree = html.fromstring(response_text)
                for element in tree.xpath('//div/a[normalize-space(text())]'):
                    text = element.text.strip()
                    href = element.get('href', '').strip()
                    if href and not any(word in text for word in words_to_remove):
                        versions[text] = href
                        year_math = re.match(r'^\d{4}', text.strip())
                        if year_math:
                            year = year_math.group(0)
                            if year not in ['Carregando', 'Carregando...']:
                                years.append(year)
                return versions, years
            except Exception as proxy_e:
                logger.warning(f'Falha ao tentar com proxies após timeout inicial: {proxy_e}')
                return []

        except Exception as e:
            logger.warning(f'Erro inesperado na função principal: {e}')
            return []