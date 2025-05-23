import re
from scrapers.icarros import (
    scraper_automakers as ic_automakers,
    scraper_models as ic_models,
    scraper_technical_sheet as ic_technical
)
from db.mongo import insert_vehicle, insert_vehicle_specs
from runners.common import validate_scraper_data
from logger.logger import get_logger

logger = get_logger('icarros', 'icarros')

async def run_icarros():
    logger.info('🚗 Iniciando scrapers do Icarros')
    reference = 'icarros'

    automakers = await ic_automakers.get_automakers()
    if not await validate_scraper_data(automakers, 'automakers', 'icarros'):
        return False

    for automaker in automakers:
        models = await ic_models.get_models(automaker)
        if not await validate_scraper_data(models, f'models para {automaker}', 'icarros'):
            continue

        for model_name, url in models.items():
            technical_data = await ic_technical.get_technical_sheet(url)
            if not await validate_scraper_data(technical_data,
                                               f'Ficha tecnica para {technical_data}','icarros'):
                continue

            equipment = {}
            version_title = technical_data['titulo']['titulo_veiculo']
            main_title = technical_data['titulo']['titulo_principal']
            anos = re.findall(r'\b\d{4}\b', main_title)
            anos = [int(ano) for ano in anos]

            if len(anos) == 2:
                year = list(range(anos[0], anos[1]+1))
            else:
                year = anos

            document = await insert_vehicle(automaker, model_name, year, version_title, reference)
            logger.info(f'Documento inserido com sucesso: {document}')
            document_specs = await insert_vehicle_specs(automaker, model_name, year,
                                                        version_title, technical_data, equipment)
            logger.info(f'Documento com especificacoes inserido com sucesso: {document_specs}')

    logger.info('✅ Finalizado Icarros')
    return True
