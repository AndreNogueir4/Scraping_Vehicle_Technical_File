import requests
from lxml import html
from unidecode import unidecode
from logger.logger import get_logger, save_log
from utils.request_with_retry_proxy import fichacompleta_proxy
from fake_useragent import UserAgent


REFERENCE = 'fichacompleta'
logger = get_logger('scraper_automakers', reference=REFERENCE)

def generate_user_agent():
    ua = UserAgent()
    return ua.random

def get_automakers():
    words_to_remove = ['Quem Somos', 'Contato', 'Política de Privacidade', 'Ver mais']

    url = 'https://www.fichacompleta.com.br/carros/marcas/'
    user_agent = generate_user_agent()

    headers = {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
        'Referer': 'https://www.fichacompleta.com.br/carros/',
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

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            tree = html.fromstring(response.text)

            error_message = tree.xpath('//text')
            if 'Digite o código:' in error_message:
                logger.warning('Captcha encontrado no scraper_automakers (fichacompleta)')
                return []

            automakers = tree.xpath('//div/a/text()')
            automakers = [
                unidecode(maker.lower().strip().replace(' ', '-'))
                for maker in automakers
                if maker.strip() and maker.strip() not in words_to_remove
            ]
            return automakers

        elif response.status_code == 403:
            logger.warning('Status_code: 403 usando proxy (scraper_automakers/fichacompleta)')
            content_proxy = fichacompleta_proxy(url, headers)
            tree = html.fromstring(content_proxy)
            automakers = tree.xpath('//div/a/text()')
            automakers = [
                unidecode(maker.lower().strip().replace(' ', '-'))
                for maker in automakers
                if maker.strip() and maker.strip() not in words_to_remove
            ]
            return automakers

        else:
            print(f'Erro ao acessar {url} - Status: {response.status_code}')
            return []

    except requests.RequestException as e:
        print(f"Erro ao fazer requisição: {e}")
        return []