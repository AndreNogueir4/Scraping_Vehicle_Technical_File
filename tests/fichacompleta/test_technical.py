import httpx
import asyncio
import pytest
from lxml import html
from fake_useragent import UserAgent


def generate_headers_user_agent(automaker, model):
    ua = UserAgent()
    referer = f'https://www.fichacompleta.com.br/carros/{automaker}/{model}/'

    headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
        'Referer': referer,
        'Connection': 'keep-alive',
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
async def get_technical_sheet(automaker, model, href):
    url = f'https://www.fichacompleta.com.br{href}'
    headers = generate_headers_user_agent(automaker, model)

    async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
        try:
            response = await client.get(url)
            response_text = response.text

            if response.status_code == 200:
                tree = html.fromstring(response_text)

                keys_dict = tree.xpath('//div[1]/b/text()')
                value_dict = tree.xpath('//div[2]/text()')
                value_dict = [value.strip() for value in value_dict if value.strip()]

                result = {title: value for title, value in zip(keys_dict, value_dict)}

                equipments = tree.xpath('//li/span/text()')
                equipments = [equip.strip() for equip in equipments if equip.strip()]

                if not equipments:
                    equipments = ['Equipment not listed for this model']

                return result, equipments

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
    Href = '/carros/chevrolet/s10-ltz-2-5-4x4-at-cd-2018'
    Result = asyncio.run(get_technical_sheet(Automaker, Model, Href))
    print(Result)