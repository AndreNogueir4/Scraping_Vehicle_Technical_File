import re
from typing import Dict, List, Tuple
from lxml import html
from .base_scraper import BaseScraper
from ..shared.schemas import VersionYear
from ..shared.exceptions import ScraperError

class VersionYearScraper(BaseScraper):
    WORDS_TO_REMOVE = [
        'Quem Somos',
        'Contato',
        'Política de Privacidade',
        'Ver mais',
        'Carregando',
        'Carregando...'
    ]

    async def get_versions_year(self, automaker: str, model: str) -> Tuple[Dict[str, str], List[str]]:
        model = self._normalize_model_slug(model)
        url = f'{self.BASE_URL}/carros/{automaker}/{model}/'

        try:
            tree = await self.fetch_page(url)
            versions, years = self._parse_versions_years(tree, automaker, model)
            self.logger.info(f'Encontradas {len(versions)} versões e {len(years)} anos para {automaker}/{model}')
            return versions, years
        except ScraperError as e:
            self.logger.error(f'Falha ao obter versões para {automaker}/{model}: {str(e)}')
            return {}, []

    def _normalize_model_slug(self, model: str) -> str:
        return (model.replace('.', '-')
                .replace(':', '-').replace(' ', '-').rstrip('-'))

    def _parse_versions(self, tree: html.HtmlElement, automaker: str, model: str) -> Tuple[Dict[str, str], List[str]]:
        versions = {}
        years = []

        for element in tree.xpath('//div/a[normalize-space(text())]'):
            text = element.text.strip()
            href = element.get('href', '').strip()

            if href and not any(word in text for word in self.WORDS_TO_REMOVE):
                versions[text] = href

                year_match = re.match(r'^\d{4}', text)
                if year_match:
                    year = year_match.group(0)
                    if year not in years:
                        years.append(year)
        return versions, years