import aiohttp
from lxml import html
from logger.logger import get_logger, save_log
from utils.request_with_retry import request_with_proxy

REFERENCE = 'carrosnaweb'
logger = get_logger('scraper_models', reference=REFERENCE)

words_to_remove = [
    'Página Principal', 'Comparativo', 'Avaliação', 'Notícias', 'Opinião do Dono', 'Concessionárias',
    'Ranking', 'Carros Mais Vendidos', 'Todos', 'Hatchback', 'Sedã', 'Perua', 'Minivan', 'Cupê',
    'Conversível', 'SUV', 'Picape', 'Van', 'Furgão', 'Jipe', 'Chassi-cabine', 'Mapa do site',
    'Sobre o site', 'Privacidade', 'Termos de uso', 'Mobile', 'Fale Conosco', 'Comunicar erro',
    'Carros mais Vendidos', 'Próximos Lançamentos', '\r\n\t\t', 'Comparativos'
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0',
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

async def fetch_models(automaker):
    url = 'https://www.carrosnaweb.com.br/catalogofabricante.asp'
    logger.info(f'Iniciando busca por modelos da montadora {automaker}')
    await save_log('INFO', 'Iniciando busca por modelos da montadora {automaker}', reference=REFERENCE)

    params = {
        'fabricante': automaker,
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

        models = tree.xpath('//a/font/text()')
        models = [model.lower() for model in models if model not in words_to_remove]
        logger.info(f"✅ {len(models)} modelos encontradas.")
        await save_log('INFO', f"✅ {len(models)} modelos encontradas.", reference=REFERENCE)
        return models

    except Exception as e:
        logger.exception(f'❌ Erro ao buscar modelos: {e}')
        await save_log('ERROR', f'❌ Erro ao buscar modelos: {e}', reference=REFERENCE)
        return []