import aiohttp
from lxml import html
from unidecode import unidecode
from logger.logger import get_logger, save_log
from utils.request_with_retry import request_with_proxy

REFERENCE = 'fichacompleta'
logger = get_logger('scraper_automakers', reference=REFERENCE)

words_to_remove = ['Quem Somos', 'Contato', 'Política de Privacidade', 'Ver mais']

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
    'Referer': 'https://www.fichacompleta.com.br/carros/',
    'Priority': 'u=0, i',
}

async def fetch_automakers():
    url = 'https://www.fichacompleta.com.br/carros/marcas/'
    logger.info('Iniciando busca por montadoras')
    await save_log('INFO', 'Iniciando busca por montadoras', reference=REFERENCE)
    
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

        automakers = tree.xpath('//div/a/text()')
        automakers = [unidecode(maker.lower().strip()) for maker in automakers if maker.strip() and maker.strip()
                      not in words_to_remove]
        logger.info(f"✅ {len(automakers)} montadoras encontradas.")
        await save_log('INFO', f"✅ {len(automakers)} montadoras encontradas.", reference=REFERENCE)
        return automakers

    except Exception as e:
        logger.exception(f'❌ Erro ao processar HTML: {e}')
        await save_log('ERROR', f'❌ Erro ao processar HTML: {e}', reference=REFERENCE)
        return []