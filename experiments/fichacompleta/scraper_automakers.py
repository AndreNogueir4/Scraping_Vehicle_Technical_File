import time
import requests
import os
from dotenv import load_dotenv
from lxml import html
from unidecode import unidecode

load_dotenv()
PROXIES = os.getenv('PROXIES', '').split(',')

headers = {
    'Host': 'www.fichacompleta.com.br',
    'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Accept-Language': 'pt-BR',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_9_7; en-US) Gecko/20100101 Firefox/53.4',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
                'q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Priority': 'u=0, i',
    'Connection': 'keep-alive',
}

def get_automakers_proxy(url, max_retries=10):
    for proxy in PROXIES:
        proxy_dict = {
            'http': proxy,
            'https': proxy
        }
        for attempt in range(1, max_retries + 1):
            try:
                print(f'Tentando proxy: {proxy} (tentativa  {attempt}/{max_retries})')
                response = requests.get(url, headers=headers, proxies=proxy_dict)

                if response.status_code == 200:
                    tree = html.fromstring(response.text)
                    all_text = tree.xpath('//text')
                    if any('Digite o código:' in text for text in all_text):
                        print('CAPTCHA ainda presente com este proxy')
                        continue
                    return response.text
                else:
                    print(f'Proxy {proxy} falhou com status {response.status_code}')
            except requests.RequestException as e:
                print(f'Erro com proxy {proxy}: {e}')
            time.sleep(3)
    raise Exception('Todos os proxies falharam ou CAPTCHA persistiu')


def get_automakers():
    words_to_remove = ['Quem Somos', 'Contato', 'Política de Privacidade', 'Ver mais']

    url = 'https://www.fichacompleta.com.br/carros/marcas/'

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:

            tree = html.fromstring(response.text)

            error_message = tree.xpath('//text()')
            if 'Digite o código:' in error_message:
                print('Captcha encontrado')
                return []

            automakers = tree.xpath('//div/a/text()')
            automakers = [
                unidecode(maker.lower().strip().replace(' ', '-'))
                for maker in automakers
                if maker.strip() and maker.strip() not in words_to_remove
            ]

            return automakers
        elif response.status_code == 403:
            print('Status_code: 403 usando proxy')
            content_proxy = get_automakers_proxy(url)
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