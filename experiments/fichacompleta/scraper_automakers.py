import requests
from lxml import html
from unidecode import unidecode

def get_automakers():
    words_to_remove = ['Quem Somos', 'Contato', 'Política de Privacidade', 'Ver mais']

    headers = {
        'Host': 'www.fichacompleta.com.br',
        'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Accept-Language': 'pt-BR',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_9_7; en-US) Gecko/20100101 Firefox/53.4',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Priority': 'u=0, i',
        'Connection': 'keep-alive',
    }

    url = 'https://www.fichacompleta.com.br/carros/marcas/'

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        tree = html.fromstring(response.text)

        error_message = tree.xpath('//text()')
        if 'Digite o código:' in error_message:
            print('Captcha encontrado')
            return []

        automakers = tree.xpath('//div/a/text()')
        automakers = [
            unidecode(maker.lower().strip())
            for maker in automakers
            if maker.strip() and maker.strip() not in words_to_remove
        ]

        return automakers

    except requests.RequestException as e:
        print(f"Erro ao fazer requisição: {e}")
        return []