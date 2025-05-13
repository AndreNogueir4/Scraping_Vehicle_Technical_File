from lxml import html
from unidecode import unidecode
from logger.logger import get_logger, save_log
from utils.get_clean_html import get_clean_html

REFERENCE = 'fichacompleta'
logger = get_logger('scraper_automakers', reference=REFERENCE)

words_to_remove = ['Quem Somos', 'Contato', 'Política de Privacidade', 'Ver mais']

headers = {
     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
    'Referer': 'https://www.fichacompleta.com.br/carros/',
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

async def fetch_automakers():
    url = 'https://www.fichacompleta.com.br/carros/marcas/'
    logger.info('Iniciando busca por montadoras')
    await save_log('INFO', 'Iniciando busca por montadoras', reference=REFERENCE)

    html_content = await get_clean_html(url, headers=headers, reference=REFERENCE)
    if not html_content:
        return []

    try:
        tree = html.fromstring(html_content)

        error_message = tree.xpath('//text()')

        if 'Digite o código:' in error_message:
            logger.error(f'⛔ CAPTCHA DETECTADO - Interrompendo execução')
            await save_log('CRITICAL', 'CAPTCHA detectado no fichacompleta', reference=REFERENCE)
            raise SystemExit("CAPTCHA Bloqueou o Acesso")

        automakers = tree.xpath('//div/a/text()')
        automakers = [unidecode(maker.lower().strip()) for maker in automakers if maker.strip() and maker.strip()
                      not in words_to_remove]
        logger.info(f"✅ {len(automakers)} montadoras encontradas.")
        await save_log('INFO', f"✅ {len(automakers)} montadoras encontradas.", reference=REFERENCE)
        return automakers

    except SystemExit:
        raise

    except Exception as e:
        logger.exception(f'❌ Erro ao processar HTML: {e}')
        await save_log('ERROR', f'❌ Erro ao processar HTML: {e}', reference=REFERENCE)
        return []