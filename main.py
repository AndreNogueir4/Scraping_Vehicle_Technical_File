import argparse
import asyncio
import sys
from logger.logger import get_logger
from db.mongo import insert_vehicle, get_vehicles_by_reference

logger = get_logger(name='main', reference='main')

from scrapers.carrosweb import (
    scraper_automakers as cw_automakers,
    scraper_models as cw_models,
    scraper_years as cw_years,
    scraper_version_link_consultation as cw_version_link,
    scraper_technical_sheet as cw_technical
)

from scrapers.fichacompleta import (
    scraper_automakers as fc_automakers,
    scraper_models as fc_models,
    scraper_version_and_years as fc_version,
    scraper_technical_sheet as fc_technical
)


async def validate_scraper_data(data, data_name, scraper_name):
    """ Valida se os dados retornados pelo scraper estao vazios """
    if not data:
        error_msg = f"⚠️ Dados vazios retornados pelo scraper {scraper_name} ({data_name})"
        logger.error(error_msg)
        return False
    return True


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


async def main():
    parser = argparse.ArgumentParser(description='Escolha qual scraper rodar')
    parser.add_argument('site', choices=['carrosnaweb', 'fichacompleta', 'full'],
                       help='Nome do site ou "full" para rodar todos')
    args = parser.parse_args()

    try:
        if args.site == 'carrosnaweb':
            success = await run_carrosnaweb()
        elif args.site == 'fichacompleta':
            success = await run_fichacompleta()
        elif args.site == 'full':
            success_cw = await run_carrosnaweb()
            success_fc = await run_fichacompleta()
            success = success_cw and success_fc

        if not success:
            logger.error("❌ Execução interrompida devido a dados vazios")
            sys.exit(1)

    except Exception as e:
        logger.error(f"⛔ Erro inesperado: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())