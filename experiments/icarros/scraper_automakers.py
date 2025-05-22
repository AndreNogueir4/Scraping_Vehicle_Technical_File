import requests

headers = {
    'Host': 'www.icarros.com.br',
    'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
    'Accept': '*/*',
    'X-Requested-With': 'XMLHttpRequest',
    'Accept-Language': 'pt-BR',
    'Sec-Ch-Ua-Mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  'Chrome/127.0.6533.100 Safari/537.36',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://www.icarros.com.br/catalogo/index.jsp',
    'Priority': 'u=1, i',
}

def get_automakers():

    response = requests.get(
        'https://www.icarros.com.br/rest/select-options/CARRO/marcas',
        headers=headers,
    )

    json_content = response.json()

    automakers = [item['nome'] for item in json_content]
    automakers = [maker.lower().replace(' ', '-').replace('(', '').replace(')', '') for maker in automakers]

    return automakers