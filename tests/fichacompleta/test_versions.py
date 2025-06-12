import httpx
import pytest
import asyncio
import re
from lxml import html
from fake_useragent import UserAgent


def generate_headers_user_agent(automaker):
    ua = UserAgent()
    reference = f'https://www.fichacompleta.com.br/carros/{automaker}/'

    headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive',
        'Referer': reference,
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

@pytest.mark.asyncio
async def get_version_years(automaker, model):
    words_to_remove = ['Quem Somos', 'Contato', 'Política de Privacidade', 'Ver mais']
    versions = {}
    years = []

    model = model.replace('.', '-').replace(':', '-').replace(' ', '-')
    if model.endswith('-'):
        model = model[:-1]

    url = f'https://www.fichacompleta.com.br/carros/{automaker}/{model}/'
    headers = generate_headers_user_agent(automaker)

    async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
        try:
            response = await client.get(url)
            response_text = response.text

            if response.status_code == 200:
                tree = html.fromstring(response_text)

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

if __name__ == '__main__':
    Automaker = 'chevrolet'
    Model = 's10'
    Result = asyncio.run(get_version_years(Automaker, Model))
    print(Result)