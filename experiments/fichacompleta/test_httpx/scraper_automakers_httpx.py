import httpx
import asyncio
import os
from dotenv import load_dotenv
from lxml import html
from unidecode import unidecode
from fake_useragent import UserAgent

load_dotenv()
PROXIES = [p.strip() for p in os.getenv('PROXIES', '').split(',') if p.strip()]

def generate_headers_user_agent():
    ua = UserAgent()
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;"
                  "q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "cache-control": "max-age=0",
        "priority": "u=0, i",
        "referer": "https://www.fichacompleta.com.br/carros/",
        "sec-ch-ua": '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": ua.random,
    }
    return headers

async def get_automakers_proxy(url, headers, max_retries=20):
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

async def get_automakers():
    words_to_remove = ["Quem Somos", "Contato", "Política de Privacidade", "Ver mais"]
    url = 'https://www.fichacompleta.com.br/carros/marcas/'
    headers = generate_headers_user_agent()

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
                        response_text = await get_automakers_proxy(url, headers)
                        tree = html.fromstring(response_text)
                    except Exception as proxy_e:
                        print(f'Falha ao tentar com proxies após CAPTCHA: {proxy_e}')
                        return []

                automakers = tree.xpath('//div/a/text()')
                automakers = [
                    unidecode(maker.lower().strip().replace(' ', '-'))
                    for maker in automakers if maker.strip() and maker.strip() not in words_to_remove
                ]
                return automakers

            elif response.status_code == 403:
                print('Status_code: 403 - Bloqueado. Tentando com proxies...')
                try:
                    response_text = await get_automakers_proxy(url, headers)
                    tree = html.fromstring(response_text)
                    automakers = tree.xpath('//div/a/text()')
                    automakers = [
                        unidecode(maker.lower().strip().replace(' ', '-'))
                        for maker in automakers if maker.strip() and maker.strip() not in words_to_remove
                    ]
                    return automakers
                except Exception as proxy_e:
                    print(f'Falha ao tentar com proxies após 403: {proxy_e}')
                    return []

            else:
                print(f'Erro inicial {response.status_code}. Tentando com proxies...')
                try:
                    response_text = await get_automakers_proxy(url, headers)
                    tree = html.fromstring(response_text)
                    automakers = tree.xpath('//div/a/text()')
                    automakers = [
                        unidecode(maker.lower().strip().replace(' ', '-'))
                        for maker in automakers if maker.strip() and maker.strip() not in words_to_remove
                    ]
                    return automakers
                except Exception as proxy_e:
                    print(f'Falha ao tentar com proxies após erro {response.status_code}: {proxy_e}')
                    return []

        except httpx.RequestError as e:
            print(f'Erro de requisição httpx na requisição inicial: {e}')
            print('Tentando com proxies devido ao erro inicial...')
            try:
                response_text = await get_automakers_proxy(url, headers)
                tree = html.fromstring(response_text)
                automakers = tree.xpath('//div/a/text()')
                automakers = [
                    unidecode(maker.lower().strip().replace(' ', '-'))
                    for maker in automakers if maker.strip() and maker.strip() not in words_to_remove
                ]
                return automakers
            except Exception as proxy_e:
                print(f'Falha ao tentar com proxies após erro inicial: {proxy_e}')
                return []

        except asyncio.TimeoutError:
            print('Timeout na requisição inicial')
            print('Tentando com proxies devido ao timeout inicial...')
            try:
                response_text = await get_automakers_proxy(url, headers)
                tree = html.fromstring(response_text)
                automakers = tree.xpath('//div/a/text()')
                automakers = [
                    unidecode(maker.lower().strip().replace(' ', '-'))
                    for maker in automakers if maker.strip() and maker.strip() not in words_to_remove
                ]
                return automakers
            except Exception as proxy_e:
                print(f'Falha ao tentar com proxies após timeout inicial: {proxy_e}')
                return []

        except Exception as e:
            print(f'Erro inesperado na função principal: {e}')
            return []