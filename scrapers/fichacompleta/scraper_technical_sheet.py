from lxml import html
from logger.logger import get_logger, save_log
from utils.get_clean_html import get_clean_html

REFERENCE = 'fichacompleta'
logger = get_logger('scraper_technical_sheet', reference=REFERENCE)

async def fetch_technical_sheet(automaker, model, year, link_query):
    url = f'https://www.fichacompleta.com.br{link_query}'
    logger.info(f'Iniciando busca pela ficha tecnica do modelo: {model} para o ano {year}')
    await save_log('INFO', f'Iniciando busca pela ficha tecnica do modelo: {model} para o ano {year}',
                   reference=REFERENCE)

    referer = f'https://www.fichacompleta.com.br/carros/{automaker}/{model}/'.strip()

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

    html_content = await get_clean_html(url, headers=headers, reference=REFERENCE)
    if not html_content:
        return []

    try:
        tree = html.fromstring(html_content)

        keys_dict = tree.xpath('//div[1]/b/text()')
        value_dict = tree.xpath('//div[2]/text()')
        value_dict = [value.strip() for value in value_dict if value.strip() and value.strip()]

        result = {title: value.strip() for title, value in zip(keys_dict, value_dict)}

        equipments = tree.xpath('//li/span/text()')
        equipments = [equip.strip() for equip in equipments if equip.strip() and equip.strip()]

        logger.info(f'✅ Informações da ficha tecnica encontradas')
        await save_log('INFO', f'✅ Informações da ficha tecnica encontradas', reference=REFERENCE)
        return result, equipments

    except Exception as e:
        logger.exception(f'❌ Erro ao buscar ficha tecnica: {e}')
        await save_log('ERROR', f'❌ ❌ Erro ao buscar ficha tecnica: {e}', reference=REFERENCE)
        return []