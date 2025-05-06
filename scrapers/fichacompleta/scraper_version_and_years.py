import aiohttp
from lxml import html
from logger.logger import get_logger, save_log
from utils.request_with_retry import request_with_proxy

REFERENCE = 'fichacompleta'
logger = get_logger('scraper_version_and_years', reference=REFERENCE)

words_to_remove = ['Quem Somos', 'Contato', 'Política de Privacidade', 'Ver mais']

async def fetch_version_and_years(automaker, model):
    url = f'https://www.fichacompleta.com.br/carros/{automaker}/{model}/'
    logger.info(f'Iniciando busca pelas versoes e anos para modelo: {model}')
    await save_log('INFO', f'Iniciando busca pelas versoes e anos para modelo: {model}',
                   reference=REFERENCE)

    referer = f'https://www.fichacompleta.com.br/carros/{automaker}/'

    headers = {
        'Host': 'www.fichacompleta.com.br',
        'Cache-Control': 'max-age=0',
        'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Accept-Language': 'pt-BR',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      'Chrome/127.0.6533.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
                  'q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': referer,
        'Priority': 'u=0, i',
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    html_content = await response.text()
                else:
                    raise Exception(f'Status ruim: {response.status}')

        except Exception as e:
            logger.warning(f'⚠️ Erro sem proxy: {e}')
            await save_log('WARNING', f'⚠️ Erro sem proxy: {e}', reference=REFERENCE)
            logger.info('Tentando buscar com proxy')
            html_content = await request_with_proxy(url, headers=headers)

            if not html_content:
                logger.error('❌ Falha mesmo usando proxy.')
                await save_log('ERROR', '❌ Falha mesmo usando proxy.', reference=REFERENCE)
                return []

    try:
        tree = html.fromstring(html_content)
        error_message = tree.xpath('//text()')

        if any("Digite o código:" in msg for msg in error_message):
            logger.warning('⚠️ Deu ruim, mensagem de erro encontrada!')
            await save_log('WARNING', '⚠️ Erro detectado na página.', reference=REFERENCE)
            return []

        versions = {}
        for element in tree.xpath('//div/a'):
            text = element.text.strip()
            href = element.get('href')
            if text and not any(word in text for word in words_to_remove):
                versions[text] = href

        years = []
        for version in versions:
            parts = version.split(' · ')
            year = parts[0]
            years.append(year)

        logger.info(f"✅ {len(versions)} versoes e anos encontrados para {model}.")
        await save_log('INFO', f"✅ {len(versions)} versoes e anos encontrados para {model}.",
                       reference=REFERENCE)
        return versions, years

    except Exception as e:
        logger.exception(f'❌ Erro ao buscar anos e versoes: {e}')
        await save_log('ERROR', f'❌ Erro ao buscar anos e versoes: {e}', reference=REFERENCE)
        return []