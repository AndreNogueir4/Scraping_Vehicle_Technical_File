import asyncio
from typing import List, Dict
from scraper_automaker import get_automakers
from scraper_models import get_models
from scraper_years import get_years

async def process_automaker(automaker: str) -> Dict[str, List[str]]:

    print(f'Processando fabricante: {automaker}')
    models = await get_models(automaker)

    model_task = []
    for model in models:
        model_task.append(get_years(automaker, model))

    years_by_model = await asyncio.gather(*model_task)

    return {model: years for model, years in zip(models, years_by_model)}

async def main(automakers: List[str]):

    tasks = [process_automaker(automaker) for automaker in automakers]
    results = await asyncio.gather(*tasks)

    return {automaker: result for automaker, result in zip(automakers, results)}


if __name__ == '__main__':

    automakers = get_automakers()
    final_result = asyncio.run(main(automakers))

    for automaker, models in final_result.items():
        print(f'\nFabricante: {automaker}')
        for model, years in models.items():
            print(f'  Modelo: {model} - Anos: {', '.join(years)}')