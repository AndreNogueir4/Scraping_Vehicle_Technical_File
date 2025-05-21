import asyncio
from experiments.fichacompleta.scraper_automakers import get_automakers
from experiments.fichacompleta.scraper_models import get_models
from experiments.fichacompleta.scraper_version_and_years import get_version_years
from experiments.fichacompleta.request_technical_sheet import get_technical_sheet


async def main():
    automakers = get_automakers()

    if not automakers:
        print('A lista de automakers está vazia!')
        return

    for automaker in automakers:
        models = get_models(automaker)

        for model in models:
            version, years = get_version_years(automaker, model)

            for href in version.values():
                result, equipments = get_technical_sheet(automaker, model, href)

                print(f'Montadora: {automaker} | Modelo: {model} | Versoes: {version} | Anos: {years}')
                print(f'Ficha Tecnica: {result} | Equipamentos do modelo: {equipments}')

if __name__ == '__main__':
    asyncio.run(main())