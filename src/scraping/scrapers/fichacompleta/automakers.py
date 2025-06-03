from unidecode import unidecode
from lxml import html
from .base_scraper import BaseScraper
from ..shared.schemas import Automaker

class AutomakerScraper(BaseScraper):
    WORDS_TO_REMOVE = [
        'Quem Somos',
        'Contato',
        'Política de Privacidade',
        'Ver mais'
    ]

    async def get_automakers(self) -> list[Automaker]:
        url = f'{self.BASE_URL}/carros/marcas/'

        try:
            tree = await self.fetch_page(url)
            automakers = self._parse_automakers(tree)
            self.logger.info(f'Encontradas {len(automakers)} marcas')
            return automakers
        except Exception as e:
            self.logger.error(f'Falha ao obter marcas: {str(e)}')
            return []

    def _parse_automakers(self, tree: html.HtmlElement) -> list[Automaker]:
        raw_automakers = tree.xpath('//div/a/text()')

        processed = []
        for maker in raw_automakers:
            maker = maker.strip()
            if maker and maker not in self.WORDS_TO_REMOVE:
                url_slug = unidecode(maker.lower().replace(' ', '-'))

                processed.append(Automaker(
                    name=maker,
                    url_slug=url_slug,
                    source=self.REFERENCE,
                    url=f'{self.BASE_URL}/carros/{url_slug}/'
                ))
        return processed