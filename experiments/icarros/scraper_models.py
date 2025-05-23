import aiohttp
from lxml import html

headers = {
    'Host': 'www.icarros.com.br',
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
    'Referer': 'https://www.icarros.com.br/catalogo/index.jsp',
    'Priority': 'u=0, i',
}

async def get_models(automaker):
    url = f'https://www.icarros.com.br/{automaker}'

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:

            html_content = await response.text()
            tree = html.fromstring(html_content)

            links = tree.xpath('//li/div/a')
            result = {}

            for link in links:
                href = link.get('href')
                title = link.get('title')
                if title and href:
                    result[title] = href

            return result