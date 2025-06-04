import asyncio
import re
from typing import List, Dict, Optional
from ..fichacompleta.automakers import AutomakerScraper
from ..fichacompleta.models import ModelScraper
from ..fichacompleta.versions_years import VersionYearScraper
from ..fichacompleta.technical_sheet import TechnicalSheetScraper
from src.db.repositories.vehicle import VehicleRepository
from src.db.repositories.specs import TechnicalSpecsRepository
from logger import get_logger
from src.utils.validators import validate_scraped_data

logger = get_logger('fichacompleta_runner')

class FichaCompletaRunner:
    def __init__(self):
        self.vehicle_repo = VehicleRepository()
        self.specs_repo = TechnicalSpecsRepository()
        self.reference = 'fichacompleta'

    async def run(self) -> bool:
        logger.info('🚗 Iniciando scrapers do Ficha Completa')

        try:
            automakers = await self._get_automakers()
            if not automakers:
                return False

            for automaker in automakers:
                await self._process_automaker(automaker)

            logger.info('✅ Finalizado scraping do Ficha Completa com sucesso')
            return True
        except Exception as e:
            logger.error(f'❌ Erro fatal no FichaCompletaRunner: {str(e)}', exc_info=True)
            return False

    async def _get_automakers(self) -> List[Dict]:
        async with AutomakerScraper() as scraper:
            automakers = await scraper.get_automakers()

            if not validate_scraped_data(automakers, 'automakers', self.reference):
                logger.error('Nenhuma marca válida encontrada')
                return []

            logger.info(f'Encontradas {len(automakers)} marcas')
            return automakers

    async def _process_automaker(self, automaker: Dict):
        logger.info(f'🔧 Processando marca: {automaker["name"]}')

        async with ModelScraper() as scraper:
            models = await scraper.get_models(automaker['url_slug'])

            if not validate_scraped_data(models, f'models para {automaker["name"]}', self.reference):
                logger.warning(f'Pulando marca {automaker["name"]} - sem modelos válidos')
                return

            for model in models:
                await self._process_model(automaker, model)

    async def _process_model(self, automaker: Dict, model: Dict):
        logger.info(f'🛠️ Processando modelo: {automaker["name"]} {model["name"]}')

        async with VersionYearScraper() as scraper:
            versions, years = await scraper.get_versions_year(
                automaker['url_slug'],
                model['url_slug']
            )

            if not validate_scraped_data(versions, 'versions', self.reference) or \
                    not validate_scraped_data(years, 'years', self.reference):
                logger.warning(f'Pulando modelo {model["name"]} - sem versões válidas')
                return

            for version_name, version_url in versions.items():
                await self._process_version(automaker, model, version_name, version_url)

    async def _process_version(self, automaker: Dict, model: Dict, version_name: str, version_url: str):
        vehicle_id = await self._save_vehicle(automaker, model, version_name)
        if not vehicle_id:
            return

        await self._save_technical_specs(vehicle_id, automaker, model, version_name, version_url)

    async def _save_vehicle(self, automaker: Dict, model: Dict, version: str) -> Optional[str]:
        try:
            year_match = re.search(r'^\d{4}', version)
            year = year_match.group(0) if year_match else '0000'

            vehicle_data = {
                'automaker': automaker['name'],
                'model': model['name'],
                'year': year,
                'version': version,
                'reference': self.reference,
                'source_url': model.get('url', '')
            }

            existing = await self.vehicle_repo.find_by_fields(vehicle_data)
            if existing:
                logger.debug(f'Veículo já existe: {vehicle_data}')
                return existing['_id']

            result = await self.vehicle_repo.insert(vehicle_data)
            logger.info(f'✅ Veículo inserido: {automaker["name"]} {model["name"]} {version}')
            return result.inserted_id
        except Exception as e:
            logger.error(f'Erro ao salvar veículo: {str(e)}')
            return None

    async def _save_technical_specs(self, vehicle_id: str, automaker: Dict, model: Dict,
                                    version: str, version_url: str):
        try:
            async with TechnicalSheetScraper() as scraper:
                sheet = await scraper.get_technical_sheet(
                    automaker['url_slug'],
                    model['url_slug'],
                    version_url
                )

                if not sheet.specifications:
                    logger.warning(f'Ficha técnica vazia para {version_url}')
                    return

                specs_data = {
                    'vehicle_id': vehicle_id,
                    'specifications': sheet.specifications,
                    'equipment': sheet.equipment,
                    'source_url': version_url,
                    'reference': self.reference
                }

                await self.specs_repo.upsert(
                    {'vehicle_id': vehicle_id},
                    specs_data
                )
                logger.info(f'📝 Ficha técnica salva para {automaker["name"]} {model["name"]} {version}')
        except Exception as e:
            logger.error(f'Erro ao obter ficha técnica: {str(e)}')


async def run_fichacompleta():
    runner = FichaCompletaRunner()
    return await runner.run()


if __name__ == '__main__':
    asyncio.run(run_fichacompleta())