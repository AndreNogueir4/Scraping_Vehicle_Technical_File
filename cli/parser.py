import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Escolha qual scraper rodar')
    parser.add_argument('site', choices=['carrosweb', 'fichacompleta', 'icarros', 'full'],
                        help='Nome do site ou "full" para rodar todos')
    return parser.parse_args()