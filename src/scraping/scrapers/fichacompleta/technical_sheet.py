from typing import Dict, List, Tuple
from lxml import html
from .base_scraper import BaseScraper
from ..shared.schemas import TechnicalSheet
from ..shared.exceptions import ScraperError

class TechnicalSheetScraper(BaseScraper):
    async def get_technical_sheet(self, automaker: str, model: str, href: str) -> TechnicalSheet:
        url = f'{self.BASE_URL}{href}'

        try:
            tree = await self.fetch_page(url)
            specs, equipment = self._parse_technical_sheet(tree)

            version = href.split('/')[-1]

            return TechnicalSheet(
                specifications=specs,
                equipment=equipment,
                source_url=url,
                automaker=automaker,
                model=model,
                version=version
            )

        except ScraperError as e:
            self.logger.error(f'Falha ao obter ficha técnica para {url}: {str(e)}')
            return TechnicalSheet(
                specifications={},
                equipment=['Erro ao obter equipamentos'],
                source_url=url,
                automaker=automaker,
                model=model,
                version='unknown'
            )

    def _parse_technical_sheet(self, tree: html.HtmlElement) -> Tuple[Dict[str, str], List[str]]:
        keys = tree.xpath('//div[1]/b/text()')
        values = [v.strip() for v in tree.xpath('//div[2]/text()') if v.strip()]
        specs = dict(zip(keys, values))

        equipment = [
            eq.strip() for eq in tree.xpath('//li/span/text()')
            if eq.strip()
        ] or ['Equipamentos não listados para esse modelo']

        return specs, equipment