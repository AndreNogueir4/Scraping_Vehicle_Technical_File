import aiohttp
from lxml import html
from logger.logger import get_logger
from utils.request_with_retry_proxy import icarros_proxy
from fake_useragent import UserAgent

REFERENCE = 'icarros'
logger = get_logger('scraper_models', reference=REFERENCE)

def generate_user_agent():
    ua = UserAgent()
    return ua.random

async def get_models(automaker):
    url = f'https://www.icarros.com.br/{automaker}'
    user_agent = generate_user_agent()

    headers = {
        'Host': 'www.icarros.com.br',
        'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Accept-Language': 'pt-BR',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
                  'q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://www.icarros.com.br/catalogo/index.jsp',
        'Priority': 'u=0, i',
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:

            if response.status == 200:
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

            else:
                response_proxy = await icarros_proxy(url, headers)

                html_content = await response_proxy.text()
                tree = html.fromstring(html_content)

                links = tree.xpath('//li/div/a')
                result = {}

                for link in links:
                    href = link.get('href')
                    title = link.get('title')
                    if title and href:
                        result[title] = href

                return result