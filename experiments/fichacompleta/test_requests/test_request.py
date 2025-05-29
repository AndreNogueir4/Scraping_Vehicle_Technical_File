from scraper_automakers import get_automakers
from scraper_models import get_models
from scraper_version_and_years import get_version_years
from db.mongo_experiments import insert_vehicle

def process_model(automaker, model):
    versions, years = get_version_years(automaker, model)
    print(f'\nAutomaker: {automaker}')
    print(f'Model: {model}')
    print(f'Versions: {versions}')
    print(f'Years: {years}')

    for (version_key, version_link), year in zip(versions.items(), years):
        document = insert_vehicle(automaker, model, version_key, year, version_link, reference='fichacompleta')
        return document

    return {
        'automaker': automaker,
        'model': model,
        'versions': versions,
        'years': years
    }

def process_automaker(automaker):
    models = get_models(automaker)
    print(f'\nAutomaker: {automaker} -> Models: {models}')
    results = []
    for model in models:
        result = process_model(automaker, model)
        results.append(result)
    return results

def main():
    automakers = get_automakers()
    print(f'Automakers: {automakers}')

    all_results = []
    for automaker in automakers:
        automaker_results = process_automaker(automaker)
        all_results.extend(automaker_results)

    print('\n\n=== Final Results ===')
    for item in all_results:
        print(item)

if __name__ == '__main__':
    main()