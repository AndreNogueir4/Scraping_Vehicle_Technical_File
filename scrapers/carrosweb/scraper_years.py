import aiohttp
from lxml import html
from logger.logger import get_logger, save_log
from utils.request_with_retry import request_with_proxy

REFERENCE = 'carrosnaweb'
logger = get_logger('scraper_years', reference=REFERENCE)

words_to_remove = [
    'Página Principal', 'Comparativo', 'Avaliação', 'Notícias', 'Opinião do Dono', 'Concessionárias',
    'Ranking', 'Carros Mais Vendidos', 'Todos', 'Hatchback', 'Sedã', 'Perua', 'Minivan', 'Cupê',
    'Conversível', 'SUV', 'Picape', 'Van', 'Furgão', 'Jipe', 'Chassi-cabine', 'Mapa do site',
    'Sobre o site', 'Privacidade', 'Termos de uso', 'Mobile', 'Fale Conosco', 'Comunicar erro',
    'Carros mais Vendidos', 'Próximos Lançamentos', '\r\n\t\t', 'Comparativos'
]

async def fetch_years(automaker, model):
    url = 'https://www.carrosnaweb.com.br/catalogomodelo.asp'
    logger.info(f'Iniciando busca pelos anos para modelo: {model}')
    await save_log('INFO', f'Iniciando busca pelos anos para modelo: {model}', reference=REFERENCE)

    referer = f'https://www.carrosnaweb.com.br/catalogofabricante.asp?fabricante={automaker}'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive',
        'Referer': referer,
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'DNT': '1',
        'Sec-GPC': '1',
        'Priority': 'u=0, i',
    }

    params = {
        'fabricante': automaker,
        'modelo': model,
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    html_content = await response.text()
                else:
                    raise Exception(f'Status ruim: {response.status}')

        except Exception as e:
            logger.warning(f'⚠️ Erro sem proxy: {e}')
            await save_log('WARNING', f'⚠️ Erro sem proxy: {e}', reference=REFERENCE)
            logger.info('Tentando buscr com proxy')
            html_content = await request_with_proxy(url, headers=headers, params=params)

            if not html_content:
                logger.error('❌ Falha mesmo usando proxy.')
                await save_log('ERROR', '❌ Falha mesmo usando proxy.', reference=REFERENCE)
                return []

    try:
        tree = html.fromstring(html_content)
        error_message = tree.xpath('//text()')

        if any("Ocorreu um erro." in msg for msg in error_message):
            logger.warning('⚠️ Deu ruim, mensagem de erro encontrada!')
            await save_log('WARNING', '⚠️ Erro detectado na página.', reference=REFERENCE)
            return []

        years = tree.xpath('//a/font/text()')
        years = [year.lower() for year in years if year not in words_to_remove]
        logger.info(f"✅ {len(years)} anos encontrados para {model}.")
        await save_log('INFO', f"✅ {len(years)} anos encontrados para {model}.", reference=REFERENCE)
        return years

    except Exception as e:
        logger.exception(f'❌ Erro ao buscar anos: {e}')
        await save_log('ERROR', f'❌ Erro ao buscar anos: {e}', reference=REFERENCE)
        return []