import httpx
import asyncio
from lxml import html
from fake_useragent import UserAgent
from logger.logger import get_logger
from utils.fichacompleta.get_proxy import get_proxy

REFERENCE = 'fichacompleta'
logger = get_logger('scraper_technical_sheet', reference=REFERENCE)

def generate_headers_user_agent(automaker, model):
    ua = UserAgent()
    referer = f'https://www.fichacompleta.com.br/carros/{automaker}/{model}/'

    headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
        'Referer': referer,
        'Connection': 'keep-alive',
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

async def get_technical_sheet(automaker, model, href):
    url = f'https://www.fichacompleta.com.br{href}'
    headers = generate_headers_user_agent(automaker, model)

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

                keys_dict = tree.xpath('//div[1]/b/text()')
                value_dict = tree.xpath('//div[2]/text()')
                value_dict = [value.strip() for value in value_dict if value.strip()]

                result = {title: value for title, value in zip(keys_dict, value_dict)}

                equipments = tree.xpath('//li/span/text()')
                equipments = [equip.strip() for equip in equipments if equip.strip()]

                if not equipments:
                    equipments = ['Equipamentos nao listados para esse modelo']

                return result, equipments

            elif response.status_code == 403:
                logger.warning('Status_code: 403 - Bloqueado. Tentando com proxies...')
                try:
                    response_text = await get_proxy(url, headers)
                    tree = html.fromstring(response_text)

                    keys_dict = tree.xpath('//div[1]/b/text()')
                    value_dict = tree.xpath('//div[2]/text()')
                    value_dict = [value.strip() for value in value_dict if value.strip()]

                    result = {title: value for title, value in zip(keys_dict, value_dict)}

                    equipments = tree.xpath('//li/span/text()')
                    equipments = [equip.strip() for equip in equipments if equip.strip()]

                    if not equipments:
                        equipments = ['Equipamentos nao listados para esse modelo']

                    return result, equipments
                except Exception as proxy_e:
                    logger.warning(f'Falha ao tentar com proxies após 403: {proxy_e}')
                    return []

            else:
                logger.warning(f'Erro inicial {response.status_code}. Tentando com proxies...')
                try:
                    response_text = await get_proxy(url, headers)
                    tree = html.fromstring(response_text)

                    keys_dict = tree.xpath('//div[1]/b/text()')
                    value_dict = tree.xpath('//div[2]/text()')
                    value_dict = [value.strip() for value in value_dict if value.strip()]

                    result = {title: value for title, value in zip(keys_dict, value_dict)}

                    equipments = tree.xpath('//li/span/text()')
                    equipments = [equip.strip() for equip in equipments if equip.strip()]

                    if not equipments:
                        equipments = ['Equipamentos nao listados para esse modelo']

                    return result, equipments
                except Exception as proxy_e:
                    logger.warning(f'Falha ao tentar com proxies após erro {response.status_code}: {proxy_e}')
                    return []

        except httpx.RequestError as e:
            logger.warning(f'Erro de requisição httpx na requisição inicial: {e}')
            logger.info('Tentando com proxies devido ao erro inicial...')
            try:
                response_text = await get_proxy(url, headers)
                tree = html.fromstring(response_text)

                keys_dict = tree.xpath('//div[1]/b/text()')
                value_dict = tree.xpath('//div[2]/text()')
                value_dict = [value.strip() for value in value_dict if value.strip()]

                result = {title: value for title, value in zip(keys_dict, value_dict)}

                equipments = tree.xpath('//li/span/text()')
                equipments = [equip.strip() for equip in equipments if equip.strip()]

                if not equipments:
                    equipments = ['Equipamentos nao listados para esse modelo']

                return result, equipments
            except Exception as proxy_e:
                logger.warning(f'Falha ao tentar com proxies após erro inicial: {proxy_e}')
                return []

        except asyncio.TimeoutError:
            logger.warning('Timeout na requisição inicial')
            logger.info('Tentando com proxies devido ao timeout inicial...')
            try:
                response_text = await get_proxy(url, headers)
                tree = html.fromstring(response_text)

                keys_dict = tree.xpath('//div[1]/b/text()')
                value_dict = tree.xpath('//div[2]/text()')
                value_dict = [value.strip() for value in value_dict if value.strip()]

                result = {title: value for title, value in zip(keys_dict, value_dict)}

                equipments = tree.xpath('//li/span/text()')
                equipments = [equip.strip() for equip in equipments if equip.strip()]

                if not equipments:
                    equipments = ['Equipamentos nao listados para esse modelo']

                return result, equipments
            except Exception as proxy_e:
                logger.warning(f'Falha ao tentar com proxies após timeout inicial: {proxy_e}')
                return []

        except Exception as e:
            logger.warning(f'Erro inesperado na função principal: {e}')
            return []