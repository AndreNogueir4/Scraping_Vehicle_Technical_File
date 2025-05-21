import requests
import os
from dotenv import load_dotenv
from lxml import html
from fake_useragent import UserAgent

load_dotenv()
PROXIES = os.getenv('PROXIES', '').split(',')

automakers = 'chevrolet'
models = 'onix'
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

def get_years(automaker, model, max_retries=5):
    url = 'https://www.carrosnaweb.com.br/catalogomodelo.asp'
    referer = f'https://www.carrosnaweb.com.br/catalogofabricante.asp?fabricante={automaker}'
    user_agent = generate_user_agent()

    headers = {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive',
        'Referer': referer,
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'DNT': '1',
        'Sec-GPC': '1',
        'Priority': 'u=0, i',
    }

    params = {
        'fabricante': automaker,
        'modelo': model
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


get_years(automakers, models)