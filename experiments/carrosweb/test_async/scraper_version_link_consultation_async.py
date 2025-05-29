import aiohttp
import asyncio
import os
import re
import unicodedata
from dotenv import load_dotenv
from lxml import html
from fake_useragent import UserAgent

load_dotenv()
PROXIES = [p.strip() for p in os.getenv('PROXIES', '').split(',') if p.strip()]

def generate_headers_user_agent():
    ua = UserAgent()
    headers = {
        'Host': 'www.carrosnaweb.com.br',
        'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Accept-Language': 'pt-BR',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
                  'q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Priority': 'u=0, i',
        'Connection': 'keep-alive',
    }
    return headers

async def get_version_link_proxy(session, url, headers, params, max_retries=5):
    if not PROXIES:
        print('Nenhum proxy configurado para tentar')
        raise Exception('Tentativa de usar proxies falhou: nenhum proxy fornecido')

    for proxy in PROXIES:
        print(f'Tentando proxy: {proxy}')
        for attempt in range(1, max_retries + 1):
            try:
                print(f'Tentativa {attempt}/{max_retries} com proxy {proxy}')
                async with session.get(url, headers=headers, params=params, proxy=proxy, timeout=30.0) as response:
                    response_text = await response.text()
                    print(f'Status com proxy {proxy}: {response.status}')

                    if response.status == 200:
                        tree = html.fromstring(response_text)
                        all_text = tree.xpath('//text()')
                        if any('Ocorreu um erro.' in text for text in all_text):
                            print(f'CAPTCHA ainda presente com proxy {proxy}')
                            continue
                        print(f'Sucesso com proxy: {proxy}')
                        return response_text
                    else:
                        print(f'Proxy {proxy} falhou com status {response.status}')

            except aiohttp.ClientError as e:
                print(f'Erro de cliente aiohttp com proxy {proxy} (tentativa {attempt}): {e}')
            except asyncio.TimeoutError:
                print(f'Timeout com proxy {proxy} (tentativa {attempt})')
            except Exception as e:
                print(f'Erro inesperado com proxy {proxy} (tentativa {attempt}): {e}')

            if attempt < max_retries:
                await asyncio.sleep(5)

        print(f'Falha em todas as tentativa com proxy {proxy} ou CAPTCHA encontrado')
    raise Exception('Todos os proxies falharam ou CAPTCHA persistiu apos todas as tentativas')

async def get_versions_link(automaker, model, year):
    url = 'https://www.carrosnaweb.com.br/m/catalogo.asp'
    headers = generate_headers_user_agent()
    model = ''.join(c for c in unicodedata.normalize('NFD', model) if not unicodedata.combining(c))
    params = {'fabricante': automaker, 'varnome': model, 'anoini': year, 'anofim': year}

    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            async with session.get(url, params=params, timeout=30.0) as response:
                response_text = await response.text()
                print(f'Status sem proxy: {response.status}')

                if response.status == 200:
                    tree = html.fromstring(response_text)
                    all_text = tree.xpath('//text()')
                    if any('Ocorreu um erro.' in text for text in all_text):
                        print('Captcha encontrado na resposta inicial, tentando proxies...')
                        try:
                            response_text = await get_version_link_proxy(session, url, headers, params)
                            tree = html.fromstring(response_text)
                        except Exception as proxy_e:
                            print(f'Falha ao tentar com proxies após CAPTCHA: {proxy_e}')
                            return []

                    links = tree.xpath('//font/a')
                    versions = {}

                    for link in links:
                        href = link.get('href')
                        texto = link.text_content().strip()
                        texto = re.sub(r'\s+', ' ', texto).strip()
                        if href and texto and href.startswith('fichadetalhe.asp?codigo'):
                            versions[texto] = href

                    return versions

                elif response.status == 403:
                    print('Status_code: 403 - Bloqueado. Tentando com proxies...')
                    try:
                        response_text = await get_version_link_proxy(session, url, headers, params)
                        tree = html.fromstring(response_text)
                        links = tree.xpath('//font/a')
                        versions = {}

                        for link in links:
                            href = link.get('href')
                            texto = link.text_content().strip()
                            texto = re.sub(r'\s+', ' ', texto).strip()
                            if href and texto and href.startswith('fichadetalhe.asp?codigo'):
                                versions[texto] = href

                        return versions
                    except Exception as proxy_e:
                        print(f'Falha ao tentar com proxies após 403: {proxy_e}')
                        return []

                else:
                    print(f'Erro inicial {response.status}. Tentando com proxies...')
                    try:
                        response_text = await get_version_link_proxy(session, url, headers, params)
                        tree = html.fromstring(response_text)
                        links = tree.xpath('//font/a')
                        versions = {}

                        for link in links:
                            href = link.get('href')
                            texto = link.text_content().strip()
                            texto = re.sub(r'\s+', ' ', texto).strip()
                            if href and texto and href.startswith('fichadetalhe.asp?codigo'):
                                versions[texto] = href

                        return versions
                    except Exception as proxy_e:
                        print(f'Falha ao tentar com proxies após erro {response.status}: {proxy_e}')
                        return []

        except aiohttp.ClientError as e:
            print(f'Erro de cliente aiohttp na requisição inicial: {e}')
            print('Tentando com proxies devido ao erro inicial...')
            try:
                response_text = await get_version_link_proxy(session, url, headers, params)
                tree = html.fromstring(response_text)
                links = tree.xpath('//font/a')
                versions = {}

                for link in links:
                    href = link.get('href')
                    texto = link.text_content().strip()
                    texto = re.sub(r'\s+', ' ', texto).strip()
                    if href and texto and href.startswith('fichadetalhe.asp?codigo'):
                        versions[texto] = href

                return versions
            except Exception as proxy_e:
                print(f'Falha ao tentar com proxies após timeout inicial: {proxy_e}')
                return []

        except Exception as e:
            print(f'Erro inesperado na função principal: {e}')
            return []