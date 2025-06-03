import argparse
import asyncio
from scraper_automakers_httpx import get_automakers
from scraper_models_httpx import get_models
from scraper_version_and_year_httpx import get_version_years
from scraper_technical_sheet_httpx import get_technical_sheet
from db.mongo_experiments import insert_vehicle, get_vehicles_by_auto_referer, insert_technical_sheet


async def process_model(automaker, model):
    versions, years = await get_version_years(automaker, model)
    print(f'\nAutomaker: {automaker}')
    print(f'Model: {model}')
    print(f'Versions: {versions}')
    print(f'Years: {years}')

    versions_items = list(versions.items())

    if len(versions_items) != len(years):
        print(f"⚠️ ATENÇÃO: Discrepância encontrada - {len(versions_items)} versões vs {len(years)} anos")
        print("Serão processados apenas os pares completos")

    num_pares = min(len(versions_items), len(years))

    tasks = []
    for i in range(num_pares):
        version_name, version_link = versions_items[i]
        year = years[i]

        print(f'Processando: {version_name} ({year}) -> {version_link}')
        tasks.append(
            insert_vehicle(
                automaker=automaker,
                model=model,
                version=version_name,
                year=year,
                consult_link=version_link,
                reference='fichacompleta'
            )
        )

    await asyncio.gather(*tasks)
    return True


async def process_automaker(automaker):
    models = await get_models(automaker)
    print(f'\nAutomaker: {automaker} -> Models: {models}')

    tasks = [process_model(automaker, model) for model in models]
    await asyncio.gather(*tasks)


async def process_technical_sheet(doc):
    automaker = doc.get('automaker')
    model = doc.get('model')
    link = doc.get('consult_link')
    if not link:
        print(f'Skipping doc without link: {doc}')
        return

    result, equipments = await get_technical_sheet(automaker, model, link)
    if result or equipments:
        technical_data = {
            'automaker': automaker,
            'model': model,
            'version': str(doc.get('version')),
            'year': str(doc.get('year')),
            'result': result,
            'equipments': equipments
        }
        await insert_technical_sheet(technical_data)
        print(f'Inserted technical sheet for: {link}')
    else:
        print(f'No technical data found for: {link}')


async def process_automaker_technical_sheets(automaker):
    documents = await get_vehicles_by_auto_referer(automaker, reference='fichacompleta')
    print(f'\nProcessing technical sheets for automaker: {automaker} - {len(documents)} documents')

    tasks = [process_technical_sheet(doc) for doc in documents]
    await asyncio.gather(*tasks)


async def main():
    parser = argparse.ArgumentParser(description='Process vehicle data and technical sheets')
    parser.add_argument('--phase', type=int, choices=[1, 2, 3],
                        help='1: Insert vehicles only, 2: Process technical sheets only, 3: Run both phases')
    parser.add_argument('--automaker', type=str, help='Process only this automaker (optional)')
    args = parser.parse_args()

    automakers = await get_automakers()

    if args.automaker:
        automakers = [am for am in automakers if am.lower() == args.automaker.lower()]
        if not automakers:
            print(f'Automaker "{args.automaker}" not found')
            return

    print(f'Automakers to process: {automakers}')

    if not args.phase or args.phase == 1 or args.phase == 3:
        print('\n=== FASE 01: Inserindo veiculos ===')
        tasks = [process_automaker(automaker) for automaker in automakers]
        await asyncio.gather(*tasks)

    if args.phase == 2 or args.phase == 3:
        print('\n=== FASE 02: Processando fichas técnicas ===')
        tasks = [process_automaker_technical_sheets(automaker) for automaker in automakers]
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())