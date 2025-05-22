import requests
import os
from dotenv import load_dotenv
from lxml import html
from fake_useragent import UserAgent

load_dotenv()
PROXIES = os.getenv('PROXIES', '').split(',')

words_to_remove = [
    'Página Principal', 'Comparativo', 'Avaliação', 'Notícias', 'Opinião do Dono', 'Concessionárias',
    'Ranking', 'Carros Mais Vendidos', 'Todos', 'Hatchback', 'Sedã', 'Perua', 'Minivan', 'Cupê',
    'Conversível', 'SUV', 'Picape', 'Van', 'Furgão', 'Jipe', 'Chassi-cabine', 'Mapa do site',
    'Sobre o site', 'Privacidade', 'Termos de uso', 'Mobile', 'Fale Conosco', 'Comunicar erro', 'Versão Clássica',
    'Carros mais Vendidos', 'Próximos Lançamentos', '\r\n\t\t', 'Comparativos', 'versão clássica', 'Versão clássica'
]

def generate_user_agent():
    ua = UserAgent()
    return ua.random

def get_automakers(max_retries=5):
    url = 'https://www.carrosnaweb.com.br/avancada.asp'
    user_agent = generate_user_agent()

    headers = {
        'User-Agent': user_agent,
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
    for attempt in range(1, max_retries + 1):
        try:
            proxies = None
            if PROXIES:
                proxy = PROXIES[attempt % len(PROXIES)]
                proxies = {
                    'http': proxy,
                    'https': proxy
                }

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                html_content = response.text
                tree = html.fromstring(html_content)
                automakers = tree.xpath('//a/font/text()')
                automakers = [maker.lower() for maker in automakers if maker not in words_to_remove]
                return automakers

            else:
                print(f"Attempt {attempt}: Status code {response.status_code}")
        except requests.RequestException as e:
            print(f'Attempt {attempt}: Error - {e}')

    return []