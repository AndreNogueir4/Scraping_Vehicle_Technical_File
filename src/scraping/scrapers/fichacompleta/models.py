from unidecode import unidecode
from lxml import html
from typing import List
from .base_scraper import BaseScraper
from ..shared.schemas import Model
from ..shared.exceptions import ScraperError

class ModelScraper(BaseScraper):
    WORDS_TO_REMOVE = [
        'Quem Somos',
        'Contato',
        'Política de Privacidade',
        'Ver mais'
    ]

    async def get_models(self, automaker: str) -> List[Model]:
        url = f'{self.BASE_URL}/carros/{automaker}/'

        try:
            tree = await self.fetch_page(url)
            models = self._parse_models(tree, automaker)
            self.logger.info(f'Encontrados {len(models)} modelos para {automaker}')
            return models
        except ScraperError as e:
            self.logger.error(f'Falha ao obter modelos para {automaker}: {str(e)}')
            return []

    def _parse_models(self, tree: html.HtmlElement, automaker: str) -> List[Model]:
        models = tree.xpath('//div/a/text()').strip()

        for model in models:
            if model and model not in self.WORDS_TO_REMOVE:
                url_slug = unidecode(model.lower().replace(' ', '-'))

                models.append(Model(
                    name=model,
                    url_slug=url_slug,
                    automaker=automaker,
                    source=self.REFERENCE,
                    url=f'{self.BASE_URL}/carros/{automaker}/{url_slug}/'
                ))
        return models