import time
import requests
import os
from lxml import html
from dotenv import load_dotenv
from logger.logger import get_logger, save_log

load_dotenv()
PROXIES = os.getenv('PROXIES', '').split(',')
REFERENCE = 'fichacompleta'
logger = get_logger('request_with_retry_proxy', reference=REFERENCE)

def fichacompleta_proxy(url, headers, max_retries=5):
    for proxy in PROXIES:
        proxy_dict = {
            'http': proxy,
            'https': proxy
        }
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f'Tentando com proxy (tentativa {attempt}/{max_retries})')
                await save_log('INFO', 'Tentando com proxy (tentativa {attempt}/{max_retries})',
                               reference=REFERENCE)

                response = requests.get(url, headers=headers, proxies=proxy_dict)

                if response.status_code == 200:
                    tree = html.fromstring(response.text)
                    all_text = tree.xpath('//text')
                    if any('Digite o código:' in text for text in all_text):
                        logger.warning('CAPTCHA ainda presente com este proxy')
                        continue
                    return response.text
                else:
                    logger.warning(f'Proxy falhou com o status: {response.status_code}')
            except requests.RequestException as e:
                logger.warning(f'Erro com proxy: {e}')
            time.sleep(10)
    raise Exception('Todos os proxies falharam ou CAPTCHA persistiu')