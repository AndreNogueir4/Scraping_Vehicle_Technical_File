import requests
import os
import time
from dotenv import load_dotenv
from lxml import html
from unidecode import unidecode
from fake_useragent import UserAgent

load_dotenv()
PROXIES = os.getenv('PROXIES', '').split(',')

def generate_headers_user_agent():
    ua = UserAgent()
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
                  'q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'referer': 'https://www.fichacompleta.com.br/carros/',
        'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': ua.random,
    }
    return headers

def get_automakers_proxy(url, headers, max_retries=5):
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
            time.sleep(5)
    raise Exception('Todos os proxies falharam ou CAPTCHA persistiu')

def get_automakers():
    words_to_remove = ['Quem Somos', 'Contato', 'Política de Privacidade', 'Ver mais']
    url = 'https://www.fichacompleta.com.br/carros/marcas/'
    headers = generate_headers_user_agent()

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
            content_proxy = get_automakers_proxy(url, headers)
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
            content_proxy = get_automakers_proxy(url, headers)
            tree = html.fromstring(content_proxy)
            automakers = tree.xpath('//div/a/text()')
            automakers = [
                unidecode(maker.lower().strip().replace(' ', '-'))
                for maker in automakers
                if maker.strip() and maker.strip() not in words_to_remove
            ]
            return automakers

    except requests.RequestException as e:
        print(f'Erro ao fazer requisicao: {e}')
        return []