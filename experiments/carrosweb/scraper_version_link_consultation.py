import requests
import os
from dotenv import load_dotenv
from lxml import html
from fake_useragent import UserAgent

load_dotenv()
PROXIES = os.getenv('PROXIES', '').split(',')

automakers = 'chevrolet'
models = 'onix'
years = '2015'
words_to_remove = [
    'Página Principal', 'Comparativo', 'Avaliação', 'Notícias', 'Opinião do Dono', 'Concessionárias',
    'Ranking', 'Carros Mais Vendidos', 'Todos', 'Hatchback', 'Sedã', 'Perua', 'Minivan', 'Cupê',
    'Conversível', 'SUV', 'Picape', 'Van', 'Furgão', 'Jipe', 'Chassi-cabine', 'Mapa do site',
    'Sobre o site', 'Privacidade', 'Termos de uso', 'Mobile', 'Fale Conosco', 'Comunicar erro',
    'Carros mais Vendidos', 'Próximos Lançamentos', '\r\n\t\t', 'Comparativos'
]

def generate_user_agent():
    ua = UserAgent()
    return ua.random

def get_version_link_consultation(automaker, model, year, max_retries=5):
    url = 'https://www.carrosnaweb.com.br/catalogomodelo.asp'
    user_agent = generate_user_agent()

    headers = {
        'Host': 'www.carrosnaweb.com.br',
        'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Accept-Language': 'pt-BR',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
                  'q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Priority': 'u=0, i',
        'Connection': 'keep-alive',
    }

    params = {
        'fabricante': automaker,
        'varnome': model,
        'anoini': year,
        'anofim': year,
    }

    for proxy in PROXIES:
        proxy_dict = {
            'http': proxy,
            'https': proxy
        }
        for attempt in range(1, max_retries + 1):
            try:
                response = requests.get(url, headers=headers, params=params, proxies=proxy_dict)

                if response.status_code == 200:
                    html_content = response.text
                    print(html_content)
                else:
                    print(response.status_code)
            except requests.RequestException as e:
                print(f'Erro com proxy {proxy}: {e}')


get_version_link_consultation(automakers, models, years)