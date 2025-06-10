import asyncio
from scrapers.fichacompleta import (
    scraper_automakers as fc_automakers,
    scraper_models as fc_models,
    scraper_version_and_years as fc_version,
    scraper_technical_sheet as fc_technical
)
from db.mongo import insert_vehicle, get_vehicles_by_reference, insert_vehicle_specs, sheet_code_exists
from runners.common import validate_scraper_data
from utils.generate_sheet_code import generate_unique_sheet_code
from logger.logger import get_logger

logger = get_logger('fichacompleta', 'fichacompleta')
semaphore = asyncio.Semaphore(5)

async def run_fichacompleta(phase=3):
    logger.info('🚗 Starting Full Sheet scrapers (fichacompleta)')
    reference = 'fichacompleta'

    automakers = await fc_automakers.get_automakers()
    if not await validate_scraper_data(automakers, "automakers", "fichacompleta"):
        return False

    async def process_model(automaker, model):
        async with semaphore:
            versions, years = await fc_version.get_version_years(automaker, model)
            if not await validate_scraper_data(versions, f'versions para {automaker}/{model}',
                                               'fichacompleta') or not await validate_scraper_data(
                years, f'years para {automaker}/{model}', 'fichacompleta'):
                return

            versions_items = list(versions.items())
            num_pares = min(len(versions_items), len(years))

            tasks = []
            for i in range(num_pares):
                version_name, version_link = versions_items[i]
                year = years[i]
                tasks.append(insert_vehicle(automaker, model, year, version_name, reference))
            await asyncio.gather(*tasks)

    async def process_automaker(automaker):
        models = await fc_models.get_models(automaker)
        if not await validate_scraper_data(models, f'models para {automaker}', 'fichacompleta'):
            return
        await asyncio.gather(*[process_model(automaker, model) for model in models])

    if phase in [1, 3]:
        await asyncio.gather(*[process_automaker(automaker) for automaker in automakers])

    if phase in [2, 3]:
        vehicles = await get_vehicles_by_reference(reference)

        async def process_vehicle(vehicle):
            async with semaphore:
                vehicle_id = vehicle['_id']
                automaker = vehicle['automaker']
                model = vehicle['model']
                version_key = vehicle['version']
                year = vehicle['year']

                versions, _ = await fc_version.get_version_years(automaker, model)
                link_query = versions.get(version_key)
                if link_query:
                    result, equipments = await fc_technical.get_technical_sheet(automaker, model, link_query)
                    if result or equipments:
                        sheet_code = await generate_unique_sheet_code(sheet_code_exists)
                        technical_data = {
                            'sheet_code': sheet_code,
                            'automaker': automaker,
                            'model': model,
                            'version': str(version_key),
                            'year': str(year),
                            'result': result,
                            'equipments': equipments
                        }
                        await insert_vehicle_specs(technical_data, vehicle_id)
                        logger.info(f'Technical sheet inserted for: {link_query}')
                    else:
                        logger.warning(f'No technical data found for: {link_query}')
                else:
                    logger.warning(f'Link not found for version: {version_key}')

        await asyncio.gather(*[process_vehicle(vehicle) for vehicle in vehicles])

    logger.info('✅ Completed Complete Sheet')
    return True