import aiohttp
import asyncio
from playwright.async_api import async_playwright
from typing import Optional, Dict, Any

automaker = 'adamo'
url = f'https://www.fichacompleta.com.br/carros/{automaker}/'

PROXY = 'http://sergio_sousa_infocar_com_br:Comp12345-country-BR@la.residential.rayobyte.com:8000'

headers = {
    'Host': 'www.fichacompleta.com.br',
    'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Accept-Language': 'pt-BR',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  'Chrome/127.0.6533.100 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
              'q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Referer': 'https://www.fichacompleta.com.br/carros/marcas/',
    'Priority': 'u=0, i',
}


def parse_proxy(proxy_url: str) -> Optional[Dict[str, Any]]:
    """Parse proxy URL into Playwright compatible format"""
    if not proxy_url:
        return None

    if proxy_url.startswith('http://'):
        proxy_url = proxy_url[7:]
    elif proxy_url.startswith('https://'):
        proxy_url = proxy_url[8:]

    if '@' in proxy_url:
        auth_part, server_part = proxy_url.split('@')
        username, password = auth_part.split(':')
        return {
            'server': server_part,
            'username': username,
            'password': password
        }
    else:
        return {
            'server': proxy_url
        }


async def fetch_with_playwright():
    proxy_config = parse_proxy(PROXY)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            proxy=proxy_config
        )
        page = await browser.new_page()
        await page.goto(url)
        content = await page.content()
        await browser.close()
        print("Playwright usado com proxy")
        return content


async def fetch_html():
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, proxy=PROXY) as response:
                if response.status == 200:
                    print("AIOHTTP usado com proxy")
                    return await response.text()
                elif response.status == 403:
                    return await fetch_with_playwright()
                else:
                    print(f"Erro HTTP: {response.status}")
                    return None
    except Exception as e:
        print(f"Erro de conexão: {e}")
        return None


async def main():
    html = await fetch_html()
    if html:
        print(html)


if __name__ == '__main__':
    asyncio.run(main())