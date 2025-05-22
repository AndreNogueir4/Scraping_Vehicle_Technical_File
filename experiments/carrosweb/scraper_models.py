import aiohttp
import asyncio
import os
import ssl
from dotenv import load_dotenv
from lxml import html
from fake_useragent import UserAgent
from typing import List

load_dotenv()
PROXIES = os.getenv('PROXIES', '').split(',') if os.getenv('PROXIES') else []

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

async def get_models(automaker: str, max_retries: int = 3) -> List[str]:
    url = 'https://www.carrosnaweb.com.br/catalogofabricante.asp'
    params = {'fabricante': automaker}

    ssl_context = ssl.create_default_context()
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2

    timeout = aiohttp.ClientTimeout(
        total=60,
        connect=60,
        sock_connect=60,
        sock_read=60
    )

    headers = {
        'User-Agent': generate_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
        'Referer': 'https://www.carrosnaweb.com.br/avancada.asp',
        'Connection': 'keep-alive'
    }

    for attempt in range(1, max_retries + 1):
        try:
            async with aiohttp.ClientSession(
                    headers=headers,
                    timeout=timeout,
                    connector=aiohttp.TCPConnector(ssl=ssl_context)
            ) as session:

                try:
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            try:
                                content = await response.text(encoding='utf-8')
                            except UnicodeDecodeError:
                                content = await response.text(encoding='iso-8859-1')

                            tree = html.fromstring(content)
                            models = tree.xpath('//a/font/text()')
                            return [
                                model.strip().lower()
                                for model in models
                                if model.strip() and model.strip() not in words_to_remove
                            ]
                        else:
                            print(f"Tentativa {attempt}: Status {response.status}")
                            await asyncio.sleep(2 ** attempt)

                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    print(f"Tentativa {attempt}: Erro de conexão - {str(e)}")
                    await asyncio.sleep(2 ** attempt)
                    continue

        except Exception as e:
            print(f"Tentativa {attempt}: Erro inesperado - {str(e)}")
            await asyncio.sleep(2 ** attempt)
            continue

    return []