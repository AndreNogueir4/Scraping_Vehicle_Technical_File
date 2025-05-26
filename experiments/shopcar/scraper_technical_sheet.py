import requests
from lxml import html

words_to_remove = ['', 'DESEMPENHO', 'MOTORIZAÇÃO', 'SUSPENSÃO / FREIO / RODA', 'DIMENSÕES']

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
    'Referer': 'https://www.shopcar.com.br/fichatecnica.php?marca=2',
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

params = {
    'id': '3027',
}

response = requests.get('https://www.shopcar.com.br/fichatecnica.php', params=params, headers=headers)

html_content = response.text
tree = html.fromstring(html_content)

data = tree.xpath('//table//text()')
data = [d.strip() for d in data if d.strip() != '' and d.strip() not in words_to_remove]

print(data)