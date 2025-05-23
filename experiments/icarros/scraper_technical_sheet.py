import aiohttp
from lxml import html
from typing import Dict, Optional

words_to_remove = ['ficha técnica: ', 'N/D']

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
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Priority': 'u=0, i',
    'Connection': 'keep-alive',
}


async def get_technical_sheet(url):
    try:
        full_url = f'https://www.icarros.com.br{url}/ficha-tecnica'
        async with aiohttp.ClientSession() as session:
            async with session.get(full_url, headers=headers) as response:
                response.raise_for_status()
                html_content = await response.text()
                tree = html.fromstring(html_content)

                technical_data = {
                    'titulo': await get_titles(tree),
                    'mecanica': await get_mechanics_info(tree),
                    'dimensoes': await get_dimensions_info(tree),
                    'seguranca': await get_features(tree, 8),
                    'conforto': await get_features(tree, 10),
                    'som': await get_features(tree, 12),
                    'banco': await get_features(tree, 14),
                    'vidros': await get_features(tree, 16),
                    'outros': await get_features(tree, 18)
                }

                return technical_data

    except aiohttp.ClientError as e:
        print(f'Erro ao acessar {full_url}: {str(e)}')
        return None
    except Exception as e:
        print(f'Erro inesperado ao processar {full_url}: {str(e)}')
        return None


async def get_titles(tree) -> Dict[str, Optional[str]]:
    main_title = tree.xpath('//h1/span/text()')
    main_title = [title.strip() for title in main_title if title and title not in words_to_remove]
    main_title = ' '.join(main_title)

    vehicle_title = tree.xpath('//div/h1/text()')
    vehicle_title = [title_vehicle.strip() for title_vehicle in vehicle_title if title_vehicle.strip()]

    return {
        'titulo_principal': main_title,
        'titulo_veiculo': vehicle_title[0] if vehicle_title else None
    }


async def get_mechanics_info(tree) -> Dict[str, str]:
    raw_data = tree.xpath('//div[4]/div/table/tbody/tr/td/text()')
    cleaned_data = [info.strip() for info in raw_data if info.strip()]

    filtered_data = []
    i = 0
    while i < len(cleaned_data):
        if cleaned_data[i] == 'N/D':
            if i > 0 and cleaned_data[i - 1].startswith(('Consumo', 'Freios', 'Direção')):
                filtered_data.append(cleaned_data[i])
            i += 1
        else:
            filtered_data.append(cleaned_data[i])
            i += 1

    return await list_to_dict(filtered_data)


async def get_dimensions_info(tree) -> Dict[str, str]:
    raw_data = tree.xpath('//div[6]/div/table/tbody/tr/td/text()')
    cleaned_data = [info.strip() for info in raw_data if info.strip()]
    return await list_to_dict(cleaned_data)


async def get_features(tree, div_number: int) -> Dict[str, str]:
    items = tree.xpath(f'//div[{div_number}]/div/table/tbody/tr')
    features = {}

    for item in items:
        name_elements = item.xpath('./td[1]/text()')
        icon_elements = item.xpath('./td[2]/i/@class')

        if name_elements and icon_elements:
            name = name_elements[0].strip()
            icon = icon_elements[0]

            if 'check-circle' in icon:
                features[name] = '✅'
            elif 'times-circle' in icon:
                features[name] = '⛔'

    return features


async def list_to_dict(data_list: list) -> Dict[str, str]:
    result = {}
    i = 0
    while i < len(data_list):
        if i + 1 < len(data_list):
            result[data_list[i]] = data_list[i + 1]
            i += 2
        else:
            result[data_list[i]] = 'N/D'
            i += 1
    return result