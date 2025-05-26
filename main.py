import asyncio
import sys
from cli.parser import parse_args
from runners.carrosnaweb_runner import run_carrosnaweb
from runners.fichacompleta_runner import run_fichacompleta
from runners.icarros_runner import run_icarros
from logger.logger import get_logger

logger = get_logger('main', 'main')

async def main():
    args = parse_args()
    success = None

    try:
        if args.site == 'carrosweb':
            success = await run_carrosnaweb()
        elif args.site == 'fichacompleta':
            success = await run_fichacompleta()
        elif args.site == 'icarros':
            success = await run_icarros()
        elif args.site == 'full':
            success = await run_fichacompleta() and await run_carrosnaweb() and await run_icarros()

        if not success:
            logger.error(f'❌ Execução interrompida por erro nos dados')
            sys.exit(1)
    except Exception as e:
        logger.error(f'⛔ Erro inesperado: {e}')
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())