import httpx
import pytest
import asyncio
from lxml import html
from unidecode import unidecode
from fake_useragent import UserAgent


def generate_headers_user_agent():
    ua = UserAgent()
    headers = {
        'Host': 'www.fichacompleta.com.br',
        'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Accept-Language': 'pt-BR',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
                  'q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Purpose': 'prefetch',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://www.fichacompleta.com.br/carros/marcas/',
        'Priority': 'u=4, i',
    }
    return headers

@pytest.mark.asyncio
async def test_get_models(automaker):
    words_to_remove = ['Quem Somos', 'Contato', 'Política de Privacidade', 'Ver mais']
    url = f'https://www.fichacompleta.com.br/carros/{automaker}/'
    headers = generate_headers_user_agent()

    async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
        try:
            response = await client.get(url)
            response_text = response.text

            if response.status_code == 200:
                tree = html.fromstring(response_text)

                models = tree.xpath('//div/a/text()')
                models = [unidecode(model.lower().strip().replace(' ', '-'))
                          for model in models if model.strip() and model.strip() not in words_to_remove]
                return models

            elif response.status_code == 403:
                return []

            else:
                return []

        except httpx.RequestError as e:
            return [e]

        except asyncio.TimeoutError:
            return []

        except Exception as e:
            return [e]