import time
import requests
import os
from lxml import html
from unidecode import unidecode
from dotenv import load_dotenv

load_dotenv()
PROXIES = os.getenv('PROXIES', '').split(',')

headers = {
    'Host': 'www.fichacompleta.com.br',
    'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Accept-Language': 'pt-BR',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                    'Chrome/127.0.6533.100 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
                'q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Purpose': 'prefetch',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Dest': 'document',
    'Referer': 'https://www.fichacompleta.com.br/carros/marcas/',
    'Priority': 'u=4, i',
}

def get_models_proxy(url, max_retries=10):
    for proxy in PROXIES:
        proxy_dict = {
            'http': proxy,
            'https': proxy
        }
        for attempt in range(1, max_retries + 1):
            try:
                print(f'Tentando proxy: {proxy} (tentativa {attempt}/{max_retries})')
                response = requests.get(url, headers=headers, proxies=proxy_dict)

                if response.status_code == 200:
                    tree = html.fromstring(response.text)
                    all_text = tree.xpath('//text')
                    if any('Digite o código:' in text for text in all_text):
                        print('CAPTCHA ainda presente com este proxy')
                        continue
                    return response.text
                else:
                    print(f'Proxy {proxy} falhou com status {response.status_code} e URL: {url}')
            except requests.RequestException as e:
                print(f'Erro com proxy {proxy}: {e}')
            time.sleep(3)
    raise Exception('Todos os proxies falharam ou CAPTCHA persistiu')

def get_models(automaker):
    words_to_remove = ['Quem Somos', 'Contato', 'Política de Privacidade', 'Ver mais']

    url = f'https://www.fichacompleta.com.br/carros/{automaker}/'

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        content = response.text
        tree = html.fromstring(content)

        all_text = tree.xpath('//text')
        if any('Digite o código:' in text for text in all_text):
            print('CAPTCHA encontrado usando o proxy')
            content_proxy = get_models_proxy(url)
            tree = html.fromstring(content_proxy)

        models = tree.xpath('//div/a/text()')
        models = [unidecode(model.lower().strip().replace(' ', '-'))
                  for model in models if model.strip() and model.strip() not in words_to_remove]
        return models
    elif response.status_code == 403:
        print('Status_code: 403 usando proxy')
        content_proxy = get_models_proxy(url)
        tree = html.fromstring(content_proxy)
        models = tree.xpath('//div/a/text()')
        models = [unidecode(model.lower().strip().replace(' ', '-'))
                  for model in models if model.strip() and model.strip() not in words_to_remove]
        return models

    else:
        print(f'Erro ao acessar {url} - Status: {response.status_code}')
        return {automaker: []}