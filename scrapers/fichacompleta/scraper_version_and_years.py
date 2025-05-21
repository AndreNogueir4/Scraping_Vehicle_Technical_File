import requests
from lxml import html
import re
from logger.logger import get_logger
from utils.request_with_retry_proxy import fichacompleta_proxy
from fake_useragent import UserAgent

REFERENCE = 'fichacompleta'
logger = get_logger('scraper_version_and_years', reference=REFERENCE)

def generate_user_agent():
    ua = UserAgent()
    return ua.random

def get_version_years(automaker, model):
    words_to_remove = ['Quem Somos', 'Contato', 'Política de Privacidade', 'Ver mais']

    url = f'https://www.fichacompleta.com.br/carros/{automaker}/{model}/'
    referer = f'https://www.fichacompleta.com.br/carros/{automaker}/'
    user_agent = generate_user_agent()

    headers = {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive',
        'Referer': referer,
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'DNT': '1',
        'Sec-GPC': '1',
        'Priority': 'u=0, i',
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            tree = html.fromstring(response.text)

            error_message = tree.xpath('//text')
            if 'Digite o código:' in error_message:
                logger.warning('Captcha encontrado no scraper_version_and_years (fichacompleta)')
                return []

            versions = {}
            years = []

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

            logger.info(f"✅ {len(versions)} versoes e anos encontrados para {model}.")
            return versions, years
        elif response.status_code == 403:
            logger.warning('Status_code: 403 usando proxy (scraper_version_and_years/fichacompleta)')
            content_proxy = fichacompleta_proxy(url, headers)
            tree = html.fromstring(content_proxy)

            versions = {}
            years = []

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

            logger.info(f"✅ {len(versions)} versoes e anos encontrados para {model}.")
            return versions, years
        else:
            logger.warning(f'Erro ao acessar {url} - Status: {response.status_code}')
            return []

    except requests.RequestException as e:
        logger.warning(f'Erro ao fazer requisicao: {e}')
        return []