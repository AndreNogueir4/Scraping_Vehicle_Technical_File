import httpx
import asyncio
import re
from lxml import html
from fake_useragent import UserAgent
from logger.logger import get_logger
from utils.fichacompleta.get_proxy import get_proxy

REFERENCE = 'fichacompleta'
logger = get_logger('scraper_technical_sheet', reference=REFERENCE)

def generate_user_agent():
    ua = UserAgent()
    return ua.random

def get_technical_sheet(automaker, model, href):
    url = f'https://www.fichacompleta.com.br{href}'
    referer = f'https://www.fichacompleta.com.br/carros/{automaker}/{model}/'
    user_agent = generate_user_agent()

    headers = {
        'Host': 'www.fichacompleta.com.br',
        'Cache-Control': 'max-age=0',
        'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Accept-Language': 'pt-BR',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
                  'q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': referer,
        'Priority': 'u=0, i',
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            tree = html.fromstring(response.text)

            error_message = tree.xpath('//text')
            if 'Digite o código:' in error_message:
                logger.warning('Captcha encontrado no scraper_technical_sheet (fichacompleta)')
                return []

            keys_dict = tree.xpath('//div[1]/b/text()')
            value_dict = tree.xpath('//div[2]/text()')
            value_dict = [value.strip() for value in value_dict if value.strip() and value.strip()]

            result = {title: value.strip() for title, value in zip(keys_dict, value_dict)}

            equipments = tree.xpath('//li/span/text()')
            equipments = [equip.strip() for equip in equipments if equip.strip() and equip.strip()]

            if not equipments:
                equipments = ['Equipamentos nao listados para esse modelo']

            return result, equipments

        elif response.status_code == 403:
            logger.warning('Status_code: 403 usando proxy (scraper_version_and_years/fichacompleta)')
            content_proxy = fichacompleta_proxy(url, headers)
            tree = html.fromstring(content_proxy)

            keys_dict = tree.xpath('//div[1]/b/text()')
            value_dict = tree.xpath('//div[2]/text()')
            value_dict = [value.strip() for value in value_dict if value.strip() and value.strip()]

            result = {title: value.strip() for title, value in zip(keys_dict, value_dict)}

            equipments = tree.xpath('//li/span/text()')
            equipments = [equip.strip() for equip in equipments if equip.strip() and equip.strip()]

            if not equipments:
                equipments = ['Equipamentos nao listados para esse modelo']

            return result, equipments

        else:
            logger.warning(f'Erro ao acessar {url} - Status: {response.status_code}')
            return []

    except requests.RequestException as e:
        logger.warning(f'Erro ao fazer requisicao: {e}')
        return []