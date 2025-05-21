import requests
from lxml import html
from unidecode import unidecode
from logger.logger import get_logger
from utils.request_with_retry_proxy import fichacompleta_proxy
from fake_useragent import UserAgent

REFERENCE = 'fichacompleta'
logger = get_logger('scraper_models', reference=REFERENCE)

def generate_user_agent():
    ua = UserAgent()
    return ua.random

def get_models(automaker):
    words_to_remove = ['Quem Somos', 'Contato', 'Política de Privacidade', 'Ver mais']

    url = f'https://www.fichacompleta.com.br/carros/{automaker}/'
    user_agent = generate_user_agent()

    headers = {
        'Host': 'www.fichacompleta.com.br',
        'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Accept-Language': 'pt-BR',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
                    'q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Purpose': 'prefetch',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://www.fichacompleta.com.br/carros/marcas/',
        'Priority': 'u=4, i',
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            tree = html.fromstring(response.text)

            error_message = tree.xpath('//text')
            if 'Digite o código:' in error_message:
                logger.warning('Captcha encontrado no scraper_models (fichacompleta)')
                return []

            models = tree.xpath('//div/a/text()')
            models = [
                unidecode(model.lower().strip().replace(' ', '-'))
                for model in models if model.strip() not in words_to_remove
            ]
            logger.info(f"✅ {len(models)} modelos encontradas.")
            return models
        elif response.status_code == 403:
            logger.warning('Status_code: 403 usando proxy (scraper_models/fichacompleta)')
            content_proxy = fichacompleta_proxy(url, headers)
            tree = html.fromstring(content_proxy)
            models = tree.xpath('//div/a/text()')
            models = [
                unidecode(model.lower().strip().replace(' ', '-'))
                for model in models if model.strip() not in words_to_remove
            ]
            logger.info(f"✅ {len(models)} modelos encontradas, usando proxy")
            return models
        else:
            logger.warning(f'Erro ao acessar {url} - Status: {response.status_code}')
            return []

    except requests.RequestException as e:
        logger.warning(f'Erro ao fazer requisicao: {e}')
        return []