import aiohttp
import asyncio
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv
from lxml import html
from unidecode import unidecode

load_dotenv()

words_to_remove = ['Quem Somos', 'Contato', 'Política de Privacidade', 'Ver mais']

headers_mobile = {
    'Host': 'www.fichacompleta.com.br',
    'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?1',
    'Sec-Ch-Ua-Platform': '"Android"',
    'Accept-Language': 'pt-BR',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko)'
                  'Chrome/127.0.6533.100 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
              'q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Priority': 'u=0, i',
    'Connection': 'keep-alive',
}

headers = {
    'Host': 'www.fichacompleta.com.br',
    'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Accept-Language': 'pt-BR',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.100 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Priority': 'u=0, i',
    'Connection': 'keep-alive',
}

async def fetch_playwright(url: str, wait_time: int = 40) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko)'
                       'Chrome/127.0.6533.100 Mobile Safari/537.36'
        )
        page = await context.new_page()

        await page.goto(url)
        await asyncio.sleep(wait_time)

        content = await page.content()
        await browser.close()

        return content

async def get_automakers():
    url = 'https://www.fichacompleta.com.br/carros/marcas/'

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:

            html_content = await response.text()
            tree = html.fromstring(html_content)

            error_message = tree.xpath('//text()')

            if 'Digite o código:' in error_message:
                async with session.get(url, headers=headers_mobile) as response_mobile:
                    html_content = await response_mobile.text()
                    tree = html.fromstring(html_content)

                    error_message_mobile = tree.xpath('//text()')

                    if 'Digite o código:' in error_message_mobile:

                        html_content = await fetch_playwright(url)
                        tree = html.fromstring(html_content)

            automakers = tree.xpath('//div/a/text()')
            automakers = [unidecode(maker.lower().strip()) for maker in automakers if maker.strip() and maker.strip()
                          not in words_to_remove]

            return automakers

async def get_automakers_proxy():
    proxy_url = os.getenv('PROXIES')

    connector = None
    if proxy_url:
        connector = aiohttp.TCPConnector(ssl=False)

    async with aiohttp.ClientSession(connector=connector) as session:
            if proxy_url:
                async with session.get('https://www.fichacompleta.com.br/carros/marcas/', proxy=proxy_url,
                                       headers=headers) as response:

                    html_content = await response.text()
            else:
                print('Proxy não encontrado')

            tree = html.fromstring(html_content)

            automakers = tree.xpath('//div/a/text()')
            automakers = [unidecode(maker.lower().strip()) for maker in automakers if maker.strip() and maker.strip()
                          not in words_to_remove]

            return automakers