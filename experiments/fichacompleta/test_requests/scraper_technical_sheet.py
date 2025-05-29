import requests
import os
import time
from dotenv import load_dotenv
from lxml import html
from fake_useragent import UserAgent

load_dotenv()
PROXIES = os.getenv('PROXIES', '').split(',')

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

def get_technical_sheet_proxy(url, headers, max_retries=5):
    for proxy in PROXIES:
        proxy_dict = {
            'http': proxy,
            'https': proxy
        }
        for attempt in range(1, max_retries + 1):
            try:
                print(f'Tentando proxy: {proxy}')
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
            time.sleep(5)
    raise Exception('Todos os proxies falharam ou CAPTCHA persistiu')

def get_technical_sheet(automaker, model, href):
    url = f'https://www.fichacompleta.com.br{href}'
    headers = generate_headers_user_agent(automaker, model)

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            tree = html.fromstring(response.text)
            error_message = tree.xpath('//text()')
            if 'Digite o código:' in error_message:
                print('Captcha encontrado')
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
            print('Status_code: 403 usando proxy')
            content_proxy = get_technical_sheet_proxy(url, headers)
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
            print(f'Erro ao acessar {url} - Status: {response.status_code}')
            content_proxy = get_technical_sheet_proxy(url, headers)
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

    except requests.RequestException as e:
        print(f'Erro ao fazer requisicao: {e}')
        return []