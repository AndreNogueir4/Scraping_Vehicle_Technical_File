from scraper_automakers import get_automakers
from scraper_models import get_models

automakers = get_automakers()

for automaker in automakers:
    models_dict = get_models(automaker)

    print(models_dict)