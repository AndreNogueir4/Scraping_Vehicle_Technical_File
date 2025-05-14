import aiohttp
import asyncio
from lxml import html
from db.mongo import insert_vehicle_specs

automaker = 'chevrolet'
model = 'onix'
year = '2025'
version = 'ltz · 1.0 · turbo · at · flex'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
    'Referer': 'https://www.fichacompleta.com.br/carros/chevrolet/onix/',
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

async def fetch_and_store():
    url = 'https://www.fichacompleta.com.br/carros/chevrolet/onix-ltz-1-0-turbo-at-2025-flex'

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            html_content = await response.text()

    tree = html.fromstring(html_content)

    keys_dict = tree.xpath('//div[1]/b/text()')
    value_dict = tree.xpath('//div[2]/text()')
    value_dict = [value.strip() for value in value_dict if value.strip() and value.strip()]

    result = {title: value.strip() for title, value in zip(keys_dict, value_dict)}

    equipments = tree.xpath('//li/span/text()')
    equipments = [equip.strip() for equip in equipments if equip.strip() and equip.strip()]

    await insert_vehicle_specs(automaker, model, year, version, result, equipments)

if __name__ == '__main__':
    asyncio.run(fetch_and_store())