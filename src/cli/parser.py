import argparse
from typing import Optional, List

def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Fichas Técnicas Scraper - Escolha qual scraper executar',
        epilog='Exemplo de uso: python main.py carrosweb'
    )

    parser.add_argument(
        'site',
        choices=['carrosweb', 'fichacompleta', 'full', 'test'],
        help='Nome do site ou "full" para rodar todos. "test" para modo teste.'
    )

    return parser.parse_args(args)