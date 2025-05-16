import asyncio
from experiments.fichacompleta.scraper_automakers import get_automakers
from experiments.fichacompleta.scraper_models import fetch_all_models


async def main():
    automakers = get_automakers()

    if not automakers:
        print('A lista de automakers está vazia!')
        return

    results = await fetch_all_models(automakers)

    for result in results:
        for automaker, models in result.items():
            print(f'{automaker}: {len(models)} modelos encontrados')


if __name__ == '__main__':
    asyncio.run(main())