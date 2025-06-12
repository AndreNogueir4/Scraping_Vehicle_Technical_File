import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Choose the scraper you want to run')
    parser.add_argument('website', choices=['carrosweb', 'fichacompleta', 'full'],
                        help='Site name or "full" to run all')
    parser.add_argument('--phase', type=int, choices=[1, 2, 3], default=3,
                        help='Process phase: 1 = collect initial data, 2 = technical file, 3 = everything (default)')
    return parser.parse_args()