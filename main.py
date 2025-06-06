import asyncio
import sys
from cli.parser import parse_args
from runners.fichacompleta_runner import run_fichacompleta
from logger.logger import get_logger

logger = get_logger('main', 'main')

async def main():
    args = parse_args()
    success = None

    try:
        if args.site == 'fichacompleta':
            success = await run_fichacompleta()
        elif args.site == 'full':
            success = await run_fichacompleta()

        if not success:
            logger.error(f'❌ Execution stopped due to data error')
            sys.exit(1)
    except Exception as e:
        logger.error(f'⛔ Unexpected error: {e}')
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())