from scraper_automaker import get_automakers
from scraper_models import get_models
from scraper_years import get_years
from scraper_version_link_consultation import get_versions_link
from db.mongo_experiments import insert_vehicle

def process_model(automaker, model):
    try:
        years = get_years(automaker, model)

        for year in years:
            versions = get_versions_link(automaker, model, year)

            print(f'\nAutomaker: {automaker}')
            print(f'Model: {model}')
            print(f'Years: {year}')
            print(f'Versions: {versions}')

            if not versions:
                print(f'Nenhuma versão encontrada para {automaker} {model} {year}')
                continue

            for version_name, consult_link in versions.items():
                if not consult_link or not version_name:
                    print(f'Versão inválida encontrada: {version_name}, {consult_link}')
                    continue

                inserted_id = insert_vehicle(
                    automaker=automaker,
                    model=model,
                    version=version_name,
                    year=year,
                    consult_link=consult_link,
                    reference='carrosnaweb'
                )

                if inserted_id:
                    print(f'Veículo inserido com ID: {inserted_id}')
                else:
                    print(f'Veículo já existia: {automaker}, {model}, {version_name}, {year}')

        return True

    except Exception as e:
        print(f'Erro ao processar modelo: {model} da montadora: {automaker}: {e}')
        return None

def process_automaker(automaker):
    try:
        models = get_models(automaker)
        print(f'\nAutomaker: {automaker} -> Models: {models}')

        results = []
        for model in models:
            result = process_model(automaker, model)
            if result:
                results.append(result)

        return results

    except Exception as e:
        print(f'Erro ao processar montadora: {automaker}: {e}')
        return []

def main():
    try:
        automakers = get_automakers()
        print(f'Automakers: {automakers}')

        all_results = []
        for automaker in automakers:
            automaker_results = process_automaker(automaker)
            all_results.extend(automaker_results)

        print('\n\n=== Final Results ===')
        for item in all_results:
            print(item)

    except Exception as e:
        print(f'Erro na execução do main: {e}')

if __name__ == '__main__':
    main()