import aiohttp
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

async def get_years(automaker, model):
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

    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    try:
                        content = await response.text(encoding='utf-8')
                    except UnicodeDecodeError:
                        content = await response.text(encoding='iso-8859-1')
                else:
                    raise Exception(f'Status ruim: {response.status}')
        except Exception as e:
            print(f'Deu ruim: {e}')
            return []
    try:
        html_content = content
        tree = html.fromstring(html_content)
        years = tree.xpath('//a/font/text()')
        years = [year.lower() for year in years if year not in words_to_remove]
        return years
    except Exception as e:
        print(f'Deu ruim: {e}')
        return []