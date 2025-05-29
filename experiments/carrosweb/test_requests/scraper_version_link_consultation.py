import requests
import os
import re
import time
import unicodedata
from dotenv import load_dotenv
from lxml import html
from fake_useragent import UserAgent

load_dotenv()
PROXIES = os.getenv('PROXIES', '').split(',')

def generate_headers_user_agent():
    ua = UserAgent()

    headers = {
        'Host': 'www.carrosnaweb.com.br',
        'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Accept-Language': 'pt-BR',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
                  'q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Priority': 'u=0, i',
        'Connection': 'keep-alive',
    }
    return headers

def get_version_link_proxy(url, headers, params, max_retries=5):
    for proxy in PROXIES:
        proxy_dict = {
            'http': proxy,
            'https': proxy
        }
        for attempt in range(1, max_retries + 1):
            try:
                print(f'Tentando proxy: {proxy} (tentativa {attempt}/{max_retries})')
                response = requests.get(url, headers=headers, params=params, proxies=proxy_dict)

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

def get_versions_link(automaker, model, year):
    url = 'https://www.carrosnaweb.com.br/m/catalogo.asp'
    headers = generate_headers_user_agent()
    model = ''.join(c for c in unicodedata.normalize('NFD', model) if not unicodedata.combining(c))
    params = {'fabricante': automaker, 'varnome': model, 'anoini': year, 'anofim': year}

    try:
        response = requests.get(url, params, headers=headers)

        if response.status_code == 200:
            tree = html.fromstring(response.text)
            error_message = tree.xpath('//text()')
            if any('Ocorreu um erro.' in msg for msg in error_message):
                print('Mensagem de erro encontrada, tentando fazer a busca com proxy')
                content_proxy = get_version_link_proxy(url, headers, params)
                tree = html.fromstring(content_proxy)

            links = tree.xpath('//font/a')
            versions = {}

            for link in links:
                href = link.get('href')
                texto = link.text_content().strip()
                texto = re.sub(r'\s+', ' ', texto).strip()
                if href and texto and href.startswith('fichadetalhe.asp?codigo'):
                    versions[texto] = href

            return versions

        elif response.status_code == 403:
            print('Status_code: 403 usando proxy')
            content_proxy = get_version_link_proxy(url, headers, params)
            tree = html.fromstring(content_proxy)
            links = tree.xpath('//font/a')
            versions = {}

            for link in links:
                href = link.get('href')
                texto = link.text_content().strip()
                texto = re.sub(r'\s+', ' ', texto).strip()
                if href and texto and href.startswith('fichadetalhe.asp?codigo'):
                    versions[texto] = href

            return versions

        else:
            print(f'Erro ao acessar {url} - Status: {response.status_code}')
            content_proxy = get_version_link_proxy(url, headers, params)
            tree = html.fromstring(content_proxy)
            links = tree.xpath('//font/a')
            versions = {}

            for link in links:
                href = link.get('href')
                texto = link.text_content().strip()
                texto = re.sub(r'\s+', ' ', texto).strip()
                if href and texto and href.startswith('fichadetalhe.asp?codigo'):
                    versions[texto] = href

            return versions

    except requests.RequestException as e:
        print(f'Erro ao fazer requisição: {e}')
        return []