import aiohttp
import re
from lxml import html
from logger.logger import get_logger, save_log
from utils.request_with_retry import request_with_proxy

REFERENCE = 'carrosnaweb'
logger = get_logger('scraper_version_link_consultation', reference=REFERENCE)

words_to_remove = [
    'Página Principal', 'Comparativo', 'Avaliação', 'Notícias', 'Opinião do Dono', 'Concessionárias',
    'Ranking', 'Carros Mais Vendidos', 'Todos', 'Hatchback', 'Sedã', 'Perua', 'Minivan', 'Cupê',
    'Conversível', 'SUV', 'Picape', 'Van', 'Furgão', 'Jipe', 'Chassi-cabine', 'Mapa do site',
    'Sobre o site', 'Privacidade', 'Termos de uso', 'Mobile', 'Fale Conosco', 'Comunicar erro',
    'Carros mais Vendidos', 'Próximos Lançamentos', '\r\n\t\t', 'Comparativos'
]

headers = {
    'Host': 'www.carrosnaweb.com.br',
    'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Accept-Language': 'pt-BR',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                    'Chrome/127.0.6533.100 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
                'q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Priority': 'u=0, i',
    'Connection': 'keep-alive',
}

async def fetch_version_link_consultation(automaker, model, year):
    url = 'https://www.carrosnaweb.com.br/catalogomodelo.asp'
    logger.info(f'Iniciando busca pelas versoes e link para modelo: {model}')
    await save_log('INFO', f'Iniciando busca pelas versoes e link para modelo: {model}', reference=REFERENCE)

    params = {
        'fabricante': automaker,
        'varnome': model,
        'anoini': year,
        'anofim': year,
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

        links = tree.xpath('//font/a')
        versions = {}

        for link in links:
            href = link.get('href')
            texto = link.text_content().strip()
            texto = re.sub(r'\s+', ' ', texto).strip()

            if href and texto and href.startswith('fichadetalhe.asp?codigo'):
                versions[texto] = href
                logger.info(f'Texto: {texto} - Link: {href}')
                await save_log('INFO', f"✅ Versão: {texto} - Link: {href} encontrado.", reference=REFERENCE)

        return versions

    except Exception as e:
        logger.exception(f'❌ Erro ao buscar versoes e links: {e}')
        await save_log('ERROR', f'❌ Erro ao buscar versoes e links: {e}', reference=REFERENCE)
        return []