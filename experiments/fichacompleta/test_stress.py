import asyncio
from experiments.fichacompleta.scraper_automakers import get_automakers, get_automakers_proxy
from experiments.fichacompleta.scraper_models import get_models, get_models_proxy
from experiments.fichacompleta.scraper_version_and_years import get_version_and_years, get_version_and_years_proxy


automakers = asyncio.run(get_automakers())
if not automakers:
    print('Nenhuma montadora encontrada tentando com proxy')
    automakers = asyncio.run(get_automakers_proxy())
    if not automakers:
        print('Nenhuma montadora encontrada mesmo com proxy')

for automaker in automakers:

    models = asyncio.run(get_models(automaker))
    if not models:
        print(f'Nenhum modelo encontrado para {automaker}, tentando com proxy')
        models = asyncio.run(get_models_proxy(automaker))
        if not models:
            print(f'Nenhum modelo encontrado para {automaker}, mesmo com proxy')

    for model in models:

        versions, years = asyncio.run(get_version_and_years(automaker, model))
        if not versions and years:
            print(f'Nenhuma versão ou ano encontrado para {automaker} | {model}, tentando com proxy')
            versions, years = asyncio.run(get_version_and_years_proxy(automaker, model))
            if not versions and years:
                print(f'Nenhuma versão ou ano encontrado para {automaker} | {model}, mesmo com proxy')

        for version, year in zip(versions, years):

            print(f'Montadora: {automaker} | Modelo: {model} | Versao: {version} | Ano: {year}')