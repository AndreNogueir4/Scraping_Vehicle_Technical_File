import asyncio
import aiohttp
from lxml import html
from unidecode import unidecode

words_to_remove = ['Quem Somos', 'Contato', 'Política de Privacidade', 'Ver mais']

headers = {
    'Host': 'www.fichacompleta.com.br',
    'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Accept-Language': 'pt-BR',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.100 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Purpose': 'prefetch',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Dest': 'document',
    'Referer': 'https://www.fichacompleta.com.br/carros/marcas/',
    'Priority': 'u=4, i',
}

semaphore = asyncio.Semaphore(5)
pause_event = asyncio.Event()
pause_event.set()

async def fetch_models(session, automaker):
    await pause_event.wait()

    automaker = automaker.replace(' ', '-')
    url = f'https://www.fichacompleta.com.br/carros/{automaker}/'

    async with semaphore:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    content = await response.text()
                    tree = html.fromstring(content)

                    all_text = tree.xpath('//text()')
                    if any('Digite o código:' in text for text in all_text):
                        print(f'[CAPTCHA] Detectado em {url}')
                        pause_event.clear()
                        print("⚠️ Todas as tarefas pausadas. Resolva o CAPTCHA no navegador...")
                        input("✅ Pressione ENTER quando o CAPTCHA for resolvido para continuar...")
                        pause_event.set()
                        return await fetch_models(session, automaker)

                    models = tree.xpath('//div/a/text()')
                    models = [unidecode(model.lower().strip()) for model in models if model.strip() and model.strip()
                              not in words_to_remove]
                    return models
                else:
                    print(f'Erro ao acessar {url} - Status: {response.status}')
                    return {automaker: []}
        except Exception as e:
            print(f'Erro ao buscar {url}: {e}')
            return {automaker: []}


async def fetch_all_models(automakers: list[str]):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_models(session, automaker) for automaker in automakers]
        return await asyncio.gather(*tasks)