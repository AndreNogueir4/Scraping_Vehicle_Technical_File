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

async def run_carrosweb(phase=3):
    logger.info('🚗 Starting Full Sheet scrapers (carrosweb)')
    reference = 'carrosweb'

    automakers = await cw_automakers.get_automakers()
    if not await validate_scraper_data(automakers, 'automakers', 'carrosweb'):
        return False

    if phase in [1, 3]:
        for automaker in automakers:
            models = await cw_models.get_models(automaker)
            if not await validate_scraper_data(models, f'models para {automaker}',
                                               'carrosweb'):
                continue

            for model in models:
                years = await cw_years.get_years(automaker, model)
                if not await validate_scraper_data(years, f'years para {automaker}/{model}',
                                                   'carrosweb'):
                    continue

                for year in years:
                    version_link = cw_version_link_consultation.get_versions_link(automaker, model, year)
                    if not await validate_scraper_data(version_link,
                                                       f'version e link para {automaker}/{model}/{year}',
                                                       'carrosweb'):
                        continue

                    await insert_vehicle(automaker, model, year, version_link, reference)

    if phase in [2, 3]:
        vehicles = await get_vehicles_by_reference(reference)
        for vehicle in vehicles:
            vehicle_id = vehicle['_id']
            automaker = vehicle['automaker']
            model = vehicle['model']
            version_key = vehicle['version']
            year = vehicle['year']

            link_query = version_key

            if link_query:
                result, equipments = await cw_technical_sheet(automaker, model, year, link_query)
                if result or equipments
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

    logger.info('✅ Completed Complete Sheet')
    return True