import time
import requests
import re
import os
from dotenv import load_dotenv
from lxml import html
from fake_useragent import UserAgent

load_dotenv()
PROXIES = os.getenv('PROXIES', '').split(',')

def generate_user_agent():
    ua = UserAgent()
    return ua.random

def get_version_years_proxy(url, headers, max_retries=10):
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
            time.sleep(3)
    raise Exception('Todos os proxies falharam ou CAPTCHA persistiu')

def get_version_years(automaker, model):
    words_to_remove = ['Quem Somos', 'Contato', 'Política de Privacidade', 'Ver mais']

    versions = {}
    years = []

    url = f'https://www.fichacompleta.com.br/carros/{automaker}/{model}/'
    reference = f'https://www.fichacompleta.com.br/carros/{automaker}/'

    user_agent = generate_user_agent()

    headers = {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive',
        'Referer': reference,
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'DNT': '1',
        'Sec-GPC': '1',
        'Priority': 'u=0, i',
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        content = response.text
        tree = html.fromstring(content)

        all_text = tree.xpath('//text')
        if any('Digite o código:' in text for text in all_text):
            print('CAPTCHA encontrado usando o proxy')
            content_proxy = get_version_years_proxy(url, headers)
            tree = html.fromstring(content_proxy)

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

        return versions, years
    elif response.status_code == 403:
        print('Status_code: 403 usando proxy')
        content_proxy = get_version_years_proxy(url, headers)
        tree = html.fromstring(content_proxy)
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

        return versions, years
    else:
        print(f'Erro ao acessar {url} - Status: {response.status_code}')
        return versions, years