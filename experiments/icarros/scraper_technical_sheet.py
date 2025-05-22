import requests
from lxml import html

words_to_remove = ['ficha técnica: ', 'N/D']

headers = {
    'Host': 'www.icarros.com.br',
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

response = requests.get(
    'https://www.icarros.com.br/aston-martin/vantage/ficha-tecnica',
    headers=headers,
)

html_content = response.text
tree = html.fromstring(html_content)

title_technical_sheet = tree.xpath('//h1/span/text()')
title_technical_sheet = [title.strip() for title in title_technical_sheet if title and title not in words_to_remove]
title_technical_sheet = ' '.join(title_technical_sheet)

title_vehicle_technical_sheet = tree.xpath('//div/h1/text()')
title_vehicle_technical_sheet = [title_vehicle.strip() for title_vehicle in title_vehicle_technical_sheet if
                                 title_vehicle.strip()]

info_mechanics_technical_sheet = tree.xpath('//div[4]/div/table/tbody/tr/td/text()')
info_mechanics_technical_sheet = [info.strip() for info in info_mechanics_technical_sheet if info.strip()]

filtered_list_mechanics = []
i = 0
while i < len(info_mechanics_technical_sheet):
    if info_mechanics_technical_sheet[i] == 'N/D':
        if i > 0 and info_mechanics_technical_sheet[i-1].startswith(('Consumo', 'Freios', 'Direção')):
            filtered_list_mechanics.append(info_mechanics_technical_sheet[i])

        i += 1
    else:
        filtered_list_mechanics.append(info_mechanics_technical_sheet[i])
        i += 1

info_mechanics_dict = {}
i = 0
while i < len(filtered_list_mechanics):
    if i+1 < len(filtered_list_mechanics):
        if not filtered_list_mechanics[i+1] == 'N/D':
            info_mechanics_dict[filtered_list_mechanics[i]] = filtered_list_mechanics[i+1]
            i += 2
        else:
            info_mechanics_dict[filtered_list_mechanics[i]] = 'N/D'
            i += 1

print(title_technical_sheet)
print(title_vehicle_technical_sheet)
print(info_mechanics_technical_sheet)