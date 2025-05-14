import asyncio
import unicodedata
import re
from playwright.async_api import async_playwright
from lxml import html
from unidecode import unidecode
from fake_useragent import UserAgent

words_to_remove = ['Quem Somos', 'Contato', 'Política de Privacidade', 'Ver mais']

def remove_accent(text):
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )


async def generate_user_agent():
    ua = UserAgent()
    return ua.random


async def fetch_and_parse(url, wait_time):
    async with async_playwright() as p:
        user_agent = await generate_user_agent()
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(user_agent=user_agent)
        page = await context.new_page()

        print(f'Acessando {url} com user-agent: {user_agent}')
        await page.goto(url)

        content = await page.content()
        tree = html.fromstring(content)

        all_text = ' '.join(tree.xpath('//text()'))

        if 'Digite o código:' in all_text:
            print(f'Aguardando {wait_time} segundos para carregar a página')
            await asyncio.sleep(wait_time)
            content = await page.content()
            tree = html.fromstring(content)

        await browser.close()
        return tree


if __name__ == '__main__':
    url = 'https://www.fichacompleta.com.br/carros/marcas/'
    wait = 15.0

    tree = asyncio.run(fetch_and_parse(url, wait))

    automakers = tree.xpath('//div/a/text()')
    automakers = [unidecode(maker.lower().strip()) for maker in automakers if maker.strip() and maker.strip()
                  not in words_to_remove]
    print(automakers)

    for automaker in automakers:
        url = f'https://www.fichacompleta.com.br/carros/{automaker}/'
        tree = asyncio.run(fetch_and_parse(url, wait))

        models = tree.xpath('//div/a/text()')
        models = [unidecode(model.lower().strip()) for model in models if model.strip() and model.strip()
                  not in words_to_remove]
        print(f'Modelos para a {automaker}: {models}')

        for model in models:
            model = remove_accent(model).lower()
            url = f'https://www.fichacompleta.com.br/carros/{automaker}/{model}/'
            tree = asyncio.run(fetch_and_parse(url, wait))

            versions = {}
            years = []

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

            for version, year in zip(versions, years):
                print(f'Montadora: {automaker} | Modelo: {model} | Versao: {version} | Ano: {year}')

                version_key = version
                link_query = versions.get(version_key)

                url = f'https://www.fichacompleta.com.br{link_query}'
                print(f'Fazendo a requisição com essa URL: {url}')
                tree = asyncio.run(fetch_and_parse(url, wait))

                keys_dict = tree.xpath('//div[1]/b/text()')
                value_dict = tree.xpath('//div[2]/text()')
                value_dict = [value.strip() for value in value_dict if value.strip() and value.strip()]

                result = {title: value.strip() for title, value in zip(keys_dict, value_dict)}

                equipments = tree.xpath('//li/span/text()')
                equipments = [equip.strip() for equip in equipments if equip.strip() and equip.strip()]

                if not equipments:
                    equipments = ['Não contem lista de equipamentos para esse modelo']

                print(result)
                print(equipments)