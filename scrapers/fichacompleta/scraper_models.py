from lxml import html
from unidecode import unidecode
from logger.logger import get_logger, save_log
from utils.get_clean_html import get_clean_html

REFERENCE = 'fichacompleta'
logger = get_logger('scraper_models', reference=REFERENCE)

words_to_remove = ['Quem Somos', 'Contato', 'Política de Privacidade', 'Ver mais']

headers = {
    'Host': 'www.fichacompleta.com.br',
    'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Accept-Language': 'pt-BR',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  'Chrome/127.0.6533.100 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
              'q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Referer': 'https://www.fichacompleta.com.br/carros/marcas/',
    'Priority': 'u=0, i',
}

async def fetch_models(automaker):
    automaker = automaker.replace(' ', '-')
    url = f'https://www.fichacompleta.com.br/carros/{automaker}/'
    logger.info(f'Iniciando busca por modelos da montadora {automaker}')
    await save_log('INFO', 'Iniciando busca por modelos da montadora {automaker}', reference=REFERENCE)

    html_content = await get_clean_html(url, headers=headers, reference=REFERENCE)
    if not html_content:
        return []

    try:
        tree = html.fromstring(html_content)

        models = tree.xpath('//div/a/text()')
        models = [unidecode(model.lower().strip()) for model in models if model.strip() and model.strip()
                  not in words_to_remove]
        logger.info(f"✅ {len(models)} modelos encontradas.")
        await save_log('INFO', f"✅ {len(models)} modelos encontradas.", reference=REFERENCE)
        return models

    except Exception as e:
        logger.exception(f'❌ Erro ao buscar modelos: {e}')
        await save_log('ERROR', f'❌ Erro ao buscar modelos: {e}', reference=REFERENCE)
        return []