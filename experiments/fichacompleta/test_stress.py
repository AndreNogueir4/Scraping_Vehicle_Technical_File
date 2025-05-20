import asyncio
from experiments.fichacompleta.scraper_automakers import get_automakers
from experiments.fichacompleta.scraper_models import get_models
from experiments.fichacompleta.scraper_version_and_years import get_version_years


async def main():
    automakers = get_automakers()

    if not automakers:
        print('A lista de automakers está vazia!')
        return

    for automaker in automakers:
        models = get_models(automaker)

        for model in models:
            version, years = get_version_years(automaker, model)

            print(f'Montadora: {automaker}\nModelos: {model}\nVersion: {version}\nYears: {years}')

if __name__ == '__main__':
    asyncio.run(main())