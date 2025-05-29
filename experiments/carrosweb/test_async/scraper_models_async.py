import aiohttp
import asyncio
import os
from dotenv import load_dotenv
from lxml import html
from fake_useragent import UserAgent

load_dotenv()
PROXIES = [p.strip() for p in os.getenv('PROXIES', '').split(',') if p.strip()]

def generate_headers_user_agent():
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
        'Referer': 'https://www.carrosnaweb.com.br/avancada.asp',
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

async def get_models_proxy(session, url, headers, params, max_retries=5):
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

async def get_models(automaker):
    words_to_remove = [
        'Página Principal', 'Comparativo', 'Avaliação', 'Notícias', 'Opinião do Dono', 'Concessionárias',
        'Ranking', 'Carros Mais Vendidos', 'Todos', 'Hatchback', 'Sedã', 'Perua', 'Minivan', 'Cupê',
        'Conversível', 'SUV', 'Picape', 'Van', 'Furgão', 'Jipe', 'Chassi-cabine', 'Mapa do site',
        'Sobre o site', 'Privacidade', 'Termos de uso', 'Mobile', 'Fale Conosco', 'Comunicar erro',
        'Carros mais Vendidos', 'Próximos Lançamentos', '\r\n\t\t', 'Comparativos', 'Versão Clássica'
    ]
    url = 'https://www.carrosnaweb.com.br/catalogofabricante.asp'
    headers = generate_headers_user_agent()
    params = {'fabricante': automaker}

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
                            response_text = await get_models_proxy(session, url, headers, params)
                            tree = html.fromstring(response_text)
                        except Exception as proxy_e:
                            print(f'Falha ao tentar com proxies após CAPTCHA: {proxy_e}')
                            return []

                    models = tree.xpath('//a/font/text()')
                    return [
                        model.strip().lower()
                        for model in models
                        if model.strip() and model.strip() not in words_to_remove
                    ]

                elif response.status == 403:
                    print('Status_code: 403 - Bloqueado. Tentando com proxies...')
                    try:
                        response_text = await get_models_proxy(session, url, headers, params)
                        tree = html.fromstring(response_text)
                        models = tree.xpath('//a/font/text()')
                        return [
                            model.strip().lower()
                            for model in models
                            if model.strip() and model.strip() not in words_to_remove
                        ]
                    except Exception as proxy_e:
                        print(f'Falha ao tentar com proxies após 403: {proxy_e}')
                        return []

                else:
                    print(f'Erro inicial {response.status}. Tentando com proxies...')
                    try:
                        response_text = await get_models_proxy(session, url, headers, params)
                        tree = html.fromstring(response_text)
                        models = tree.xpath('//a/font/text()')
                        return [
                            model.strip().lower()
                            for model in models
                            if model.strip() and model.strip() not in words_to_remove
                        ]
                    except Exception as proxy_e:
                        print(f'Falha ao tentar com proxies após erro {response.status}: {proxy_e}')
                        return []

        except aiohttp.ClientError as e:
            print(f'Erro de cliente aiohttp na requisição inicial: {e}')
            print('Tentando com proxies devido ao erro inicial...')
            try:
                response_text = await get_models_proxy(session, url, headers, params)
                tree = html.fromstring(response_text)
                models = tree.xpath('//a/font/text()')
                return [
                    model.strip().lower()
                    for model in models
                    if model.strip() and model.strip() not in words_to_remove
                ]
            except Exception as proxy_e:
                print(f'Falha ao tentar com proxies após timeout inicial: {proxy_e}')
                return []

        except Exception as e:
            print(f'Erro inesperado na função principal: {e}')
            return []