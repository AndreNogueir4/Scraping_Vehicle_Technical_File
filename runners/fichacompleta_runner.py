from scrapers.fichacompleta import (
    scraper_automakers as fc_automakers,
    scraper_models as fc_models,
    scraper_version_and_years as fc_version,
    scraper_technical_sheet as fc_technical
)
from db.mongo import insert_vehicle, get_vehicles_by_reference
from runners.common import validate_scraper_data
from logger.logger import get_logger

logger = get_logger('fichacompleta', 'fichacompleta')

async def run_fichacompleta():
    logger.info('🚗 Iniciando scrapers do Ficha Completa')
    reference = 'fichacompleta'

    automakers = await fc_automakers.fetch_automakers()
    if not await validate_scraper_data(automakers, "automakers", "fichacompleta"):
        return False

    for automaker in automakers:
        models = await fc_models.fetch_models(automaker)
        if not await validate_scraper_data(models, f"models para {automaker}", "fichacompleta"):
            continue

        for model in models:
            versions, years = await fc_version.fetch_version_and_years(automaker, model)
            if not await validate_scraper_data(versions, f"versions para {automaker}/{model}",
                                               "fichacompleta") or \
               not await validate_scraper_data(years, f"years para {automaker}/{model}",
                                               "fichacompleta"):
                continue

            for version, year in zip(versions, years):
                await insert_vehicle(automaker, model, year, version, reference)

            vehicles = await get_vehicles_by_reference(reference)
            for vehicle in vehicles:
                automaker = vehicle['automaker']
                model = vehicle['model']
                year = vehicle['year']
                version_key = vehicle['version']

                link_query = versions.get(version_key)

                if link_query:
                    await fc_technical.fetch_technical_sheet(automaker, model, year, link_query)
                else:
                    logger.warning(f'Version não encontrado em versions: {version_key}')

    logger.info('✅ Finalizado Ficha Completa')
    return True