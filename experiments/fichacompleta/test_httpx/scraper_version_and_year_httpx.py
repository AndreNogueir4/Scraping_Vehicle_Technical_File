import httpx
import asyncio
import os
import re
from dotenv import load_dotenv
from lxml import html
from fake_useragent import UserAgent

load_dotenv()
PROXIES = [p.strip() for p in os.getenv('PROXIES', '').split(',') if p.strip()]

def generate_headers_user_agent(automaker):
    ua = UserAgent()
    reference = f'https://www.fichacompleta.com.br/carros/{automaker}/'

    headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive',
        'Referer': reference,
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

async def get_version_years_proxy(url, headers, max_retries=20):
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

async def get_version_years(automaker, model):
    words_to_remove = ['Quem Somos', 'Contato', 'Política de Privacidade', 'Ver mais']
    versions = {}
    years = []

    model = model.replace('.', '-').replace(':', '-').replace(' ', '-')
    if model.endswith('-'):
        model = model[:-1]

    url = f'https://www.fichacompleta.com.br/carros/{automaker}/{model}/'
    headers = generate_headers_user_agent(automaker)

    async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
        try:
            response = await client.get(url)
            response_text = response.text
            print(f'Status sem proxy: {response.status_code}')

            if response.status_code == 200:
                tree = html.fromstring(response_text)
                all_text = tree.xpath('//text()')
                if any('Digite o código:' in text for text in all_text):
                    print('Captcha encontrado na resposta inicial, tentando proxies...')
                    try:
                        response_text = await get_version_years_proxy(url, headers)
                        tree = html.fromstring(response_text)
                    except Exception as proxy_e:
                        print(f'Falha ao tentar com proxies após CAPTCHA: {proxy_e}')
                        return []

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

                return versions, years

            elif response.status_code == 403:
                print('Status_code: 403 - Bloqueado. Tentando com proxies...')
                try:
                    response_text = await get_version_years_proxy(url, headers)
                    tree = html.fromstring(response_text)
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

                    return versions, years
                except Exception as proxy_e:
                    print(f'Falha ao tentar com proxies apos 403: {proxy_e}')
                    return []

            else:
                print(f'Erro inicial {response.status_code}. Tentando com proxies...')
                try:
                    response_text = await get_version_years_proxy(url, headers)
                    tree = html.fromstring(response_text)
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

                    return versions, years
                except Exception as proxy_e:
                    print(f'Falha ao tentar com proxies apos erro {response.status_code}: {proxy_e}')
                    return []

        except httpx.RequestError as e:
            print(f'Erro de cliente httpx na requisicao inicial: {e}')
            print('Tentando com proxies devido ao erro inicial...')
            try:
                response_text = await get_version_years_proxy(url, headers)
                tree = html.fromstring(response_text)
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

                return versions, years
            except Exception as proxy_e:
                print(f'Falha ao tentar com proxies apos erro inicial: {proxy_e}')
                return []

        except asyncio.TimeoutError:
            print('Timeout na requisicao inicial')
            print('Tentando com proxies devido ao timeout inicial')
            try:
                response_text = await get_version_years_proxy(url, headers)
                tree = html.fromstring(response_text)
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

                return versions, years
            except Exception as proxy_e:
                print(f'Falha ao tentar com proxies apos timeout inicial: {proxy_e}')
                return []
        except Exception as e:
            print(f'Erro inesperado na funcao principal: {e}')
            return []
