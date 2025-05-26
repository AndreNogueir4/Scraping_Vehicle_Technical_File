import requests
import os
import re
import time
from dotenv import load_dotenv
from lxml import html
from fake_useragent import UserAgent

load_dotenv()
PROXIES = os.getenv('PROXIES', '').split(',')

def generate_headers_user_agent(automaker):
    ua = UserAgent()
    reference = f'https://www.fichacompleta.com.br/carros/{automaker}/'

    headers = {
        'User-Agent': ua.random,
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

    return headers

def get_version_years_proxy(url, headers, max_retries=5):
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

def get_version_years(automaker, model):
    words_to_remove = ['Quem Somos', 'Contato', 'Política de Privacidade', 'Ver mais']

    versions = {}
    years = []

    url = f'https://www.fichacompleta.com.br/carros/{automaker}/{model}/'
    headers = generate_headers_user_agent(automaker)

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            tree = html.fromstring(response.text)
            error_message = tree.xpath('//text()')
            if 'Digite o código:' in error_message:
                print('Captcha encontrado')
                return []

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

    except requests.RequestException as e:
        print(f'Erro ao fazer requisicao: {e}')
        return []