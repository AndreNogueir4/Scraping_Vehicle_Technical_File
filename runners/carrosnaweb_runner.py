import asyncio
from scrapers.carrosweb import (
    scraper_automakers as cw_automakers,
    scraper_models as cw_models,
    scraper_years as cw_years,
    scraper_version_link_consultation as cw_version_link_consultation,
    scraper_technical_sheet as cw_technical_sheet
)
from db.mongo import insert_vehicle, get_vehicles_by_reference, insert_vehicle_specs, sheet_code_exists
from runners.common import validate_scraper_data
from utils.generate_sheet_code import generate_unique_sheet_code
from logger.logger import get_logger

logger = get_logger('carrosweb', 'carrosweb')
semaphore = asyncio.Semaphore(5)

async def run_carrosweb(phase=3):
    logger.info('🚗 Starting Full Sheet scrapers (carrosweb)')
    reference = 'carrosweb'

    automakers = await cw_automakers.get_automakers()
    if not await validate_scraper_data(automakers, 'automakers', 'carrosweb'):
        return False

    async def process_year(automaker, model, year):
        async with semaphore:
            versions = await cw_version_link_consultation.get_versions_link(automaker, model, year)
            if not await validate_scraper_data(versions, f'versions para {automaker}/{model}/{year}', 'carrosweb'):
                return False

            tasks = [
                insert_vehicle(automaker, model, year, version_link, reference)
                for version_name, version_link in versions.items()
            ]
            await asyncio.gather(*tasks)

    async def process_model(automaker, model):
        years = await cw_years.get_years(automaker, model)
        if not await validate_scraper_data(years, f'years para {automaker}/{model}', 'carrosweb'):
            return False
        await asyncio.gather(*[process_year(automaker, model, year) for year in years])

    if phase in [1, 3]:
        model_tasks = []

        for automaker in automakers:
            models = await cw_models.get_models(automaker)
            if not await validate_scraper_data(models, f'models para {automaker}', 'carrosweb'):
                continue
            for model in models:
                model_tasks.append(process_model(automaker, model))

        await asyncio.gather(*model_tasks)

    if phase in [2, 3]:
        pass

    logger.info('✅ Completed Complete Sheet')
    return True