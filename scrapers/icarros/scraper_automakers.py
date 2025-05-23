import aiohttp
from logger.logger import get_logger
from utils.request_with_retry_proxy import icarros_proxy
from fake_useragent import UserAgent

REFERENCE = 'icarros'
logger = get_logger('scraper_automakers', reference=REFERENCE)

def generate_user_agent():
    ua = UserAgent()
    return ua.random

async def get_automakers():
    url = 'https://www.icarros.com.br/rest/select-options/CARRO/marcas'
    user_agent = generate_user_agent()

    headers = {
        'Host': 'www.icarros.com.br',
        'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
        'Accept': '*/*',
        'X-Requested-With': 'XMLHttpRequest',
        'Accept-Language': 'pt-BR',
        'Sec-Ch-Ua-Mobile': '?0',
        'User-Agent': user_agent,
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://www.icarros.com.br/catalogo/index.jsp',
        'Priority': 'u=1, i',
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:

            if response.status == 200:
                json_content = await response.json()

                automakers = [item['nome'] for item in json_content]
                automakers = [maker.lower().replace(' ', '-').replace('(', '').replace(')', '') for maker in automakers]

                return automakers

            else:
                response_proxy = await icarros_proxy(url, headers)

                json_content = response_proxy.json()
                automakers = [item['nome'] for item in json_content]
                automakers = [maker.lower().replace(' ', '-').replace('(', '').replace(')', '') for maker in automakers]

                return automakers