import aiohttp
import re
import os
from dotenv import load_dotenv
from lxml import html

load_dotenv()

words_to_remove = ['Quem Somos', 'Contato', 'Política de Privacidade', 'Ver mais']

async def get_version_and_years(automaker, model):
    url = f'https://www.fichacompleta.com.br/carros/{automaker}/{model}/'
    reference = f'https://www.fichacompleta.com.br/carros/{automaker}/'

    headers = {
        'Host': 'www.fichacompleta.com.br',
        'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Accept-Language': 'pt-BR',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': reference,
        'Priority': 'u=0, i',
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:

            html_content = await response.text()
            tree = html.fromstring(html_content)

            versions = {}
            years = []

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

async def get_version_and_years_proxy(automaker, model):
    proxy_url = os.getenv('PROXIES')
    url = f'https://www.fichacompleta.com.br/carros/{automaker}/{model}/'
    reference = f'https://www.fichacompleta.com.br/carros/{automaker}/'

    headers = {
        'Host': 'www.fichacompleta.com.br',
        'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Accept-Language': 'pt-BR',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': reference,
        'Priority': 'u=0, i',
    }

    connector = None
    if proxy_url:
        connector = aiohttp.TCPConnector(ssl=False)

    async with aiohttp.ClientSession(connector=connector) as session:
        if proxy_url:
            async with session.get(url, proxy=proxy_url) as response:

                html_content = await response.text()
        else:
            print('Proxy não encontrado')

        tree = html.fromstring(html_content)

        versions = {}
        years = []

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