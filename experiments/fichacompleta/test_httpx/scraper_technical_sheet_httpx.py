import httpx
import asyncio
import os
from dotenv import load_dotenv
from lxml import html
from fake_useragent import UserAgent

load_dotenv()
PROXIES = os.getenv('PROXIES', '').split(',')

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

async def get_technical_sheet_proxy(url, headers, max_retries=20):
    if not PROXIES:
        print('Nenhum proxy configurado para tentar')
        raise Exception('Tentativa de usar proxies falhou: nenhum proxy fornecido')

    for proxy in PROXIES:
        print(f'Tentando proxy: {proxy}')
        for attempt in range(1, max_retries + 1):
            try:
                print(f'Tentativa {attempt}/{max_retries} com proxy {proxy}')
                proxies = {
                    'http://': proxy,
                    'https://': proxy
                }

                async with httpx.AsyncClient(headers=headers, proxies=proxies, timeout=30.0) as proxy_client:
                    response = await proxy_client.get(url)
                    response_text = response.text
                    print(f'Status com proxy {proxy}: {response.status_code}')

                    if response.status_code == 200:
                        tree = html.fromstring(response_text)
                        all_text = tree.xpath('//text()')
                        if any('Digite o código:' in text for text in all_text):
                            print(f'CAPTCHA ainda presente com proxy {proxy}')
                            break
                        print(f'Sucesso com proxy: {proxy}')
                        return response_text
                    else:
                        print(f'Proxy {proxy} falhou com status {response.status_code}')

            except httpx.RequestError as e:
                print(f'Erro de requisição httpx com proxy {proxy} (tentativa {attempt}): {e}')
            except asyncio.TimeoutError:
                print(f'Timeout com proxy {proxy} (tentativa {attempt})')
            except Exception as e:
                print(f'Erro inesperado com proxy {proxy} (tentativa {attempt}): {e}')

            if attempt < max_retries:
                await asyncio.sleep(5)

        print(f'Falha em todas as tentativas com proxy {proxy} ou CAPTCHA encontrado')
    raise Exception('Todos os proxies falharam ou CAPTCHA persistiu após todas as tentativas')

async def get_technical_sheet(automaker, model, href):
    url = f'https://www.fichacompleta.com.br{href}'
    headers = generate_headers_user_agent(automaker, model)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                tree = html.fromstring(response.text)
                error_message = tree.xpath('//text()')
                if any('Digite o código:' in msg for msg in error_message):
                    print('Captcha encontrado')
                    return []

                keys_dict = tree.xpath('//div[1]/b/text()')
                value_dict = tree.xpath('//div[2]/text()')
                value_dict = [value.strip() for value in value_dict if value.strip()]

                result = {title: value for title, value in zip(keys_dict, value_dict)}

                equipments = tree.xpath('//li/span/text()')
                equipments = [equip.strip() for equip in equipments if equip.strip()]

                if not equipments:
                    equipments = ['Equipamentos nao listados para esse modelo']

                return result, equipments

            elif response.status_code == 403:
                print('Status_code: 403 usando proxy')
                content_proxy = await get_technical_sheet_proxy(url, headers)
                tree = html.fromstring(content_proxy)

                keys_dict = tree.xpath('//div[1]/b/text()')
                value_dict = tree.xpath('//div[2]/text()')
                value_dict = [value.strip() for value in value_dict if value.strip()]

                result = {title: value for title, value in zip(keys_dict, value_dict)}

                equipments = tree.xpath('//li/span/text()')
                equipments = [equip.strip() for equip in equipments if equip.strip()]

                if not equipments:
                    equipments = ['Equipamentos nao listados para esse modelo']

                return result, equipments

            else:
                print(f'Erro ao acessar {url} - Status: {response.status_code}')
                content_proxy = await get_technical_sheet_proxy(url, headers)
                tree = html.fromstring(content_proxy)

                keys_dict = tree.xpath('//div[1]/b/text()')
                value_dict = tree.xpath('//div[2]/text()')
                value_dict = [value.strip() for value in value_dict if value.strip()]

                result = {title: value for title, value in zip(keys_dict, value_dict)}

                equipments = tree.xpath('//li/span/text()')
                equipments = [equip.strip() for equip in equipments if equip.strip()]

                if not equipments:
                    equipments = ['Equipamentos nao listados para esse modelo']

                return result, equipments

        except httpx.RequestError as e:
            print(f'Erro ao fazer requisição: {e}')
            return []