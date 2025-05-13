import requests
from lxml import html
from unidecode import unidecode

words_to_remove = ['Quem Somos', 'Contato', 'Política de Privacidade', 'Ver mais']

cookies = {
    'referer': 'https%3A%2F%2Fwww.fichacompleta.com.br%2Fcarros%2Falfa-romeo%2F145%2F',
    '_ga': 'GA1.3.1677207861.1746798296',
    '_gid': 'GA1.3.1112609045.1747143175',
    'FCNEC': '%5B%5B%22AKsRol-20HEqAhnA1AxzLof8pAtZNY_Z1MYqYXejVFZqWLibmhVNIqtPDHfSRMmTgWPwmp_PfRpeU-wXA3hVkXw92dbAqsetIQn4oPjx1V6M8wm-mfrTUJrr4m7ipWy3AjpOPG-onqEqJd4u3d5DpPOa4Rhqm474xw%3D%3D%22%5D%5D',
    '__gads': 'ID=16132cbea7a4df19:T=1746798296:RT=1747143174:S=ALNI_MZhffAl5kYFejsbAwRxs3lh5EqeHA',
    '__gpi': 'UID=00000f17d21c7b8a:T=1746798296:RT=1747143174:S=ALNI_MaOVcur5hhMtKtsIV3qbgkWpN1kxQ',
    '__eoi': 'ID=ec6ae2c8defd6818:T=1746798296:RT=1747143174:S=AA-AfjYfKxtLxqPHzhEOuRwVGUXC',
    '_ga_YY4ZL6TY02': 'GS2.1.s1747143174$o2$g0$t1747143178$j0$l0$h0',
}

headers = {
    'Host': 'www.fichacompleta.com.br',
    'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Accept-Language': 'pt-BR',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.100 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Priority': 'u=0, i',
    'Connection': 'keep-alive',
}

response = requests.get('https://www.fichacompleta.com.br/carros/marcas/', headers=headers)

html_content = response.text
tree = html.fromstring(html_content)

automakers = tree.xpath('//div/a/text()')
automakers = [unidecode(maker.lower().strip()) for maker in automakers if maker.strip() and maker.strip()
              not in words_to_remove]

print(response.status_code)
print(automakers)