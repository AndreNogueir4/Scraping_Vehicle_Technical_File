import argparse
from scraper_automakers import get_automakers
from scraper_models import get_models
from scraper_version_and_years import get_version_years
from scraper_technical_sheet import get_technical_sheet
from db.mongo_experiments import insert_vehicle, get_vehicles_by_auto_referer, insert_technical_sheet

def process_model(automaker, model):
    versions, years = get_version_years(automaker, model)
    print(f'\nAutomaker: {automaker}')
    print(f'Model: {model}')
    print(f'Versions: {versions}')
    print(f'Years: {years}')

    versions_items = list(versions.items())

    if len(versions_items) != len(years):
        print(f"⚠️ ATENÇÃO: Discrepância encontrada - {len(versions_items)} versões vs {len(years)} anos")
        print("Serão processados apenas os pares completos")

    num_pares = min(len(versions_items), len(years))

    for i in range(num_pares):
        version_name, version_link = versions_items[i]
        year = years[i]

        print(f'Processando: {version_name} ({year}) -> {version_link}')
        insert_vehicle(
            automaker=automaker,
            model=model,
            version=version_name,
            year=year,
            consult_link=version_link,
            reference='fichacompleta'
        )

    return True

def process_automaker(automaker):
    models = get_models(automaker)
    print(f'\nAutomaker: {automaker} -> Models: {models}')
    for model in models:
        process_model(automaker, model)

def process_automaker_technical_sheets(automaker):
    documents = get_vehicles_by_auto_referer(automaker, reference='fichacompleta')
    print(f'\nProcessing technical sheets for automaker: {automaker} - {len(documents)} documents')

    for doc in documents:
        automaker = doc.get('automaker')
        model = doc.get('model')
        link = doc.get('consult_link')
        if not link:
            print(f'Skipping doc without link: {doc}')
            continue

        result, equipments = get_technical_sheet(automaker, model, link)
        if result or equipments:
            technical_data = {
                'automaker': automaker,
                'model': model,
                'version': str(doc.get('version')),
                'year': str(doc.get('year')),
                'result': result,
                'equipments': equipments
            }
            insert_technical_sheet(technical_data)
            print(f'Inserted technical sheet for: {link}')
        else:
            print(f'No technical data found for: {link}')


def main():
    parser = argparse.ArgumentParser(description='Process vehicle data and technical sheets')
    parser.add_argument('--phase', type=int, choices=[1, 2, 3],
                        help='1: Insert vehicles only, 2: Process technical sheets only, 3: Run both phases')
    parser.add_argument('--automaker', type=str, help='Process only this automaker (optional)')
    args = parser.parse_args()

    automakers = get_automakers()

    if args.automaker:
        automakers = [am for am in automakers if am.lower() == args.automaker.lower()]
        if not automakers:
            print(f'Automaker "{args.automaker}" not found')
            return

    print(f'Automakers to process: {automakers}')

    if not args.phase or args.phase == 1 or args.phase == 3:
        print('\n=== FASE 01: Inserindo veiculos ===')
        for automaker in automakers:
            process_automaker(automaker)

    if args.phase == 2 or args.phase == 3:
        print('\n=== FASE 02: Processando fichas técnicas ===')
        for automaker in automakers:
            process_automaker_technical_sheets(automaker)

if __name__ == '__main__':
    main()