import asyncio
from scraper_automakers_async import get_automakers
from scraper_models_async import get_models
from scraper_version_and_year_async import get_version_years
from db.mongo_experiments import insert_vehicle

async def process_model(automaker, model):
    print(f'Processando modelo: {automaker} - {model}')
    versions, years = await get_version_years(automaker, model)
    print(f'\nAutomaker: {automaker}')
    print(f'Model: {model}')
    print(f'Versions: {versions}')
    print(f'Years: {years}')

    insert_tasks = []
    for (version_key, version_link) in versions.items():
        for year in years:
            insert_tasks.append(
                insert_vehicle(automaker, model, version_key, year, version_link, reference='fichacompleta')
            )

    inserted_documents = await asyncio.gather(*insert_tasks)
    return inserted_documents

async def process_automaker(automaker):
    print(f'Processando montadora: {automaker}')
    models = await get_models(automaker)
    print(f'\nAutomaker: {automaker} -> Models: {models}')

    model_processing_tasks = []
    for model in models:
        model_processing_tasks.append(process_model(automaker, model))

    results_for_automaker = await asyncio.gather(*model_processing_tasks)
    flat_results = [item for sublist in results_for_automaker for item in sublist]
    return flat_results

async def main():
    automakers = await get_automakers()
    print(f'Automakers: {automakers}')

    automaker_processing_tasks = []
    for automaker in automakers:
        automaker_processing_tasks.append(process_automaker(automaker))

    all_results_nested = await asyncio.gather(*automaker_processing_tasks)
    all_results = [item for sublist in all_results_nested for item in sublist]

    print('\n\n=== Final Results ===')
    for item in all_results:
        print(item)

if __name__ == '__main__':
    asyncio.run(main())