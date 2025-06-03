import asyncio
import logging
from typing import Optional
from datetime import datetime
from src.db.repositories.logs import LogRepository

class MongoDBHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET, reference: Optional[str] = None):
        super().__init__(level)
        self.reference = reference
        self._log_repo = LogRepository()

    def emit(self, record):
        try:
            log_entry = self._format_log_entry(record)
            asyncio.create_task(self._save_log_async(log_entry))
        except Exception as e:
            print(f'Failed to emit log to MongoDB: {e}')

    def _format_log_entry(self, record) -> dict:
        return {
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'message': self.format(record),
            'module': record.module,
            'funcName': record.funcName,
            'lineno': record.lineno,
            'reference': self.reference
        }

    async def _save_log_async(self, log_entry: dict):
        try:
            await self._log_repo.insert_log(log_entry)
        except Exception as e:
            print(f'Failed to save log to MongoDB: {e}')