import asyncio
from scraper_automakers import get_automakers
from scraper_models import get_models
from scraper_technical_sheet import get_technical_sheet

async def main():
    print('Iniciando o scraper...')
    automakers = await get_automakers()
    print(f'Automakers encontrados: {automakers}')

    if not automakers:
        print('Nenhuma montadora encontrada')
        return

    for automaker in automakers:
        print(f'Processando montadora: {automaker}')
        models_dict = await get_models(automaker)
        print(f'Modelos encontrados para {automaker}: {models_dict}')

        if not models_dict:
            print(f'Nenhum modelo encontrado para: {automaker}')
            continue

        for model_name, url in models_dict.items():
            print(f'Buscando ficha técnica para: {model_name} ({url})')
            technical_sheet = await get_technical_sheet(url)
            print(f'Montadora: {automaker}\nModelo: {model_name}\nFicha Técnica: {technical_sheet}')

if __name__ == '__main__':
    asyncio.run(main())