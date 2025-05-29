import requests
import os
import time
from dotenv import load_dotenv
from lxml import html
from fake_useragent import UserAgent

load_dotenv()
PROXIES = os.getenv('PROXIES', '').split(',')

def generate_headers_user_agent():
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
        'Referer': 'https://www.carrosnaweb.com.br/',
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

def get_automakers_proxy(url, headers, max_retries=5):
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
                    print(f'Proxy {proxy} falhou com status {response.status_code}')
            except requests.RequestException as e:
                print(f'Erro com proxy {proxy}: {e}')
            time.sleep(5)
    raise Exception('Todos os proxies falharam ou CAPTCHA persistiu')

def get_automakers():
    words_to_remove = [
        'Página Principal', 'Comparativo', 'Avaliação', 'Notícias', 'Opinião do Dono', 'Concessionárias',
        'Ranking', 'Carros Mais Vendidos', 'Todos', 'Hatchback', 'Sedã', 'Perua', 'Minivan', 'Cupê',
        'Conversível', 'SUV', 'Picape', 'Van', 'Furgão', 'Jipe', 'Chassi-cabine', 'Mapa do site',
        'Sobre o site', 'Privacidade', 'Termos de uso', 'Mobile', 'Fale Conosco', 'Comunicar erro',
        'Carros mais Vendidos', 'Próximos Lançamentos', '\r\n\t\t', 'Comparativos', 'Versão Clássica'
    ]
    url = 'https://www.carrosnaweb.com.br/avancada.asp'
    headers = generate_headers_user_agent()

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            tree = html.fromstring(response.text)
            error_message = tree.xpath('//text()')
            if any("Ocorreu um erro." in msg for msg in error_message):
                print('Mensagem de erro')
                return []

            automakers = tree.xpath('//a/font/text()')
            automakers = [maker.lower() for maker in automakers if maker not in words_to_remove]
            return automakers

        elif response.status_code == 403:
            print('Status_code: 403 usando proxy')
            content_proxy = get_automakers_proxy(url, headers)
            tree = html.fromstring(content_proxy)
            automakers = tree.xpath('//a/font/text()')
            automakers = [maker.lower() for maker in automakers if maker not in words_to_remove]
            return automakers

        else:
            print(f'Erro ao acessar {url} - Status: {response.status_code}')
            content_proxy = get_automakers_proxy(url, headers)
            tree = html.fromstring(content_proxy)
            automakers = tree.xpath('//a/font/text()')
            automakers = [maker.lower() for maker in automakers if maker not in words_to_remove]
            return automakers

    except requests.RequestException as e:
        print(f'Erro ao fazer requisicao: {e}')
        return []