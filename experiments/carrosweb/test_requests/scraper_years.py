import requests
import os
import time
import unicodedata
from dotenv import load_dotenv
from lxml import html
from fake_useragent import UserAgent

load_dotenv()
PROXIES = os.getenv('PROXIES', '').split(',')

def generate_headers_user_agent(automaker):
    ua = UserAgent()
    referer = f'https://www.carrosnaweb.com.br/catalogofabricante.asp?fabricante={automaker}'

    headers = {
        'User-Agent': ua.random,
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
    return headers

def get_years(automaker, model):
    words_to_remove = [
        'Página Principal', 'Comparativo', 'Avaliação', 'Notícias', 'Opinião do Dono', 'Concessionárias',
        'Ranking', 'Carros Mais Vendidos', 'Todos', 'Hatchback', 'Sedã', 'Perua', 'Minivan', 'Cupê',
        'Conversível', 'SUV', 'Picape', 'Van', 'Furgão', 'Jipe', 'Chassi-cabine', 'Mapa do site',
        'Sobre o site', 'Privacidade', 'Termos de uso', 'Mobile', 'Fale Conosco', 'Comunicar erro',
        'Carros mais Vendidos', 'Próximos Lançamentos', '\r\n\t\t', 'Comparativos', 'Versão Clássica'
    ]
    url = 'https://www.carrosnaweb.com.br/catalogomodelo.asp'
    headers = generate_headers_user_agent(automaker)
    model = ''.join(c for c in unicodedata.normalize('NFD', model) if not unicodedata.combining(c))
    params = {'fabricante': automaker, 'modelo': model}

    try:
        response = requests.get(url, params, headers=headers)

        if response.status_code == 200:
            tree = html.fromstring(response.text)
            error_message = tree.xpath('//text()')
            if any('Ocorreu um erro.' in msg for msg in error_message):
                print('Mensagem de erro')
                return []

            years = tree.xpath('//a/font/text()')
            years = [year.lower() for year in years if year not in words_to_remove]
            return years

        elif response.status_code == 403:
            print('Status_code: 403 usando proxy')
            years = []
            return years

        else:
            print(f'Erro ao acessar {url} - Status: {response.status_code}')
            years = []
            return years

    except requests.RequestException as e:
        print(f'Erro ao fazer requisição: {e}')
        return []