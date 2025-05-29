import aiohttp
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
        'Host': 'www.fichacompleta.com.br',
        'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Accept-Language': 'pt-BR',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
                  'q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Purpose': 'prefetch',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://www.fichacompleta.com.br/carros/marcas/',
        'Priority': 'u=4, i',
    }
    return headers

async def get_models_proxy(session, url, headers, max_retries=5):
    if not PROXIES:
        print('Nenhum proxy configurado para tentar')
        raise Exception('Tentativa de usar proxies falhou: nenhum proxy fornecido')

    for proxy in PROXIES:
        print(f'Tentando proxy: {proxy}')
        for attempt in range(1, max_retries + 1):
            try:
                print(f'Tentativa {attempt}/{max_retries} com proxy {proxy}')
                async with session.get(url, headers=headers, proxy=proxy, timeout=30.0, ssl=False) as response:
                    response_text = await response.text()
                    print(f'Status com proxy {proxy}: {response.status}')

                    if response.status == 200:
                        tree = html.fromstring(response_text)
                        all_text = tree.xpath('//text()')
                        if any('Digite o código:' in text for text in all_text):
                            print(f'CAPTCHA ainda presente com proxy {proxy}')
                            break
                        print(f'Sucesso com proxy: {proxy}')
                        return response_text
                    else:
                        print(f'Proxy {proxy} falhou com status {response.status}')

            except aiohttp.ClientError as e:
                print(f'Erro de cliente aiohttp com proxy {proxy} (tentativa {attempt}): {e}')
            except asyncio.TimeoutError:
                print(f'Timeout com proxy {proxy} (tentaiva {attempt})')
            except Exception as e:
                print(f'Erro inesperado com proxy {proxy} (tentativa {attempt}): {e}')

            if attempt < max_retries:
                await asyncio.sleep(5)

        print(f'Falha em todas as tentativas com proxy {proxy} ou CAPTCHA encontrado')
    raise Exception('Todos os proxies falharam ou CAPTCHA persistiu apos todas as tentativas')

async def get_models(automaker):
    words_to_remove = ['Quem Somos', 'Contato', 'Política de Privacidade', 'Ver mais']
    url = f'https://www.fichacompleta.com.br/carros/{automaker}/'
    headers = generate_headers_user_agent()

    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            async with session.get(url, timeout=30.0, ssl=False) as response:
                response_text = await response.text()
                print(f'Status sem proxy: {response.status}')

                if response.status == 200:
                    tree = html.fromstring(response_text)
                    all_text = tree.xpath('//text()')
                    if any('Digite o código:' in text for text in all_text):
                        print("Captcha encontrado na resposta inicial, tentando proxies...")
                        try:
                            response_text = await get_models_proxy(session, url, headers)
                            tree = html.fromstring(response_text)
                        except Exception as proxy_e:
                            print(f"Falha ao tentar com proxies após CAPTCHA: {proxy_e}")
                            return []

                    models = tree.xpath('//div/a/text()')
                    models = [unidecode(model.lower().strip().replace(' ', '-'))
                              for model in models if model.strip() and model.strip() not in words_to_remove]
                    return models

                elif response.status == 403:
                    print('Status_code: 403 - Bloqueado. Tentando com proxies...')
                    try:
                        response_text = await get_models_proxy(session, url, headers)
                        tree = html.fromstring(response_text)
                        models = tree.xpath('//div/a/text()')
                        models = [unidecode(model.lower().strip().replace(' ', '-'))
                                  for model in models if model.strip() and model.strip() not in words_to_remove]
                        return models
                    except Exception as proxy_e:
                        print(f'Falha ao tentar com proxies apos 403: {proxy_e}')
                        return []

                else:
                    print(f"Erro inicial {response.status}. Tentando com proxies...")
                    try:
                        response_text = await get_models_proxy(session, url, headers)
                        tree = html.fromstring(response_text)
                        models = tree.xpath('//div/a/text()')
                        models = [unidecode(model.lower().strip().replace(' ', '-'))
                                  for model in models if model.strip() and model.strip() not in words_to_remove]
                        return models
                    except Exception as proxy_e:
                        print(f'Falha ao tentar com proxies apos erro {response.status}: {proxy_e}')
                        return []

        except aiohttp.ClientError as e:
            print(f'Erro de cliente aiohttp na requisicao inicial: {e}')
            print('Tentando com proxies devido ao erro inicial...')
            try:
                response_text = await get_models_proxy(session, url, headers)
                tree = html.fromstring(response_text)
                models = tree.xpath('//div/a/text()')
                models = [unidecode(model.lower().strip().replace(' ', '-'))
                          for model in models if model.strip() and model.strip() not in words_to_remove]
                return models
            except Exception as proxy_e:
                print(f'Falha ao tentar com proxies apos erro inicial: {proxy_e}')
                return []
        except asyncio.TimeoutError:
            print(f'Timeout na requisicao inicial')
            print('Tentando com proxies devido ao timeout inicial')
            try:
                response_text = await get_models_proxy(session, url, headers)
                tree = html.fromstring(response_text)
                models = tree.xpath('//div/a/text()')
                models = [unidecode(model.lower().strip().replace(' ', '-'))
                          for model in models if model.strip() and model.strip() not in words_to_remove]
                return models
            except Exception as proxy_e:
                print(f'Falha ao tentar com proxies apos timeout inicial: {proxy_e}')
                return []
        except Exception as e:
            print(f'Erro inesperado na funcao principal: {e}')
            return []