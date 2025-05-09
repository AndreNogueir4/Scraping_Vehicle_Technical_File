from scrapers.carrosweb import (
    scraper_automakers as cw_automakers,
    scraper_models as cw_models,
    scraper_years as cw_years,
    scraper_version_link_consultation as cw_version_link,
    scraper_technical_sheet as cw_technical
)
from db.mongo import insert_vehicle
from runners.common import validate_scraper_data
from logger.logger import get_logger

logger = get_logger('carrosweb', 'carrosweb')


async def run_carrosnaweb():
    logger.info('🚗 Iniciando scrapers do Carros na Web')
    reference = 'carrosnaweb'
    automakers = await cw_automakers.fetch_automakers()

    if not await validate_scraper_data(automakers, "automakers", "carrosnaweb"):
        return False

    for automaker in automakers:
        models = await cw_models.fetch_models(automaker)
        if not await validate_scraper_data(models, f"models para {automaker}", "carrosnaweb"):
            continue

        for model in models:
            years = await cw_years.fetch_years(automaker, model)
            if not await validate_scraper_data(years, f"years para {automaker}/{model}",
                                               "carrosnaweb"):
                continue

            for year in years:
                versions = await cw_version_link.fetch_version_link_consultation(automaker, model, year)
                if not await validate_scraper_data(versions, f"versions para {automaker}/{model}/{year}",
                                                   "carrosnaweb"):
                    continue

                for version in versions:
                    await insert_vehicle(automaker, model, year, version, reference)

    logger.info('✅ Finalizado Carros na Web')
    return True