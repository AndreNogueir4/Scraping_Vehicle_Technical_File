import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Escolha qual scraper rodar')
    parser.add_argument('site', choices=['carrosweb', 'fichacompleta', 'icarros', 'full'],
                        help='Nome do site ou "full" para rodar todos')
    parser.add_argument('--phase', type=int, choices=[1, 2, 3], default=3,
                        help='Fase do processo: 1 = coletar dados iniciais, 2 = ficha técnica, 3 = tudo(default)')
    return parser.parse_args()