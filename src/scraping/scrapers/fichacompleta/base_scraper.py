import httpx
import asyncio
from typing import Optional, Dict, Any
from lxml import html
from fake_useragent import UserAgent
from logger import get_logger
from ..shared.exceptions import ScraperError, BlockedError, CaptchaError
from utils.fichacompleta.get_proxy import get_proxy

class BaseScraper:
    BASE_URL = 'https://www.fichacompleta.com.br'
    REFERENCE = 'fichacompleta'

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__, reference=self.REFERENCE)
        self.client = None
        self._current_proxy = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            headers=self._generate_headers(),
            timeout=30.0,
            follow_redirects=True
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    def _generate_headers(self) -> Dict[str, str]:
        ua = UserAgent()
        return {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;"
                      "q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "max-age=0",
            "priority": "u=0, i",
            "referer": f"{self.BASE_URL}/carros/",
            "sec-ch-ua": '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": ua.random,
        }

    async def _fetch_with_retry(self, url: str, max_retries: int = 5) -> str:
        for attempt in range(max_retries):
            try:
                response = await self._try_fetch(url, attempt)
                return response
            except (BlockedError, CaptchaError) as e:
                self.logger.warning(f'Tentativa {attempt + 1} bloqueada: {str(e)}')
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)

    async def _try_fetch(self, url: str, attempt: int) -> str:
        try:
            if attempt > 0:
                response_text = await get_proxy(url, self._generate_headers())
                self.logger.info('Usando proxy para bypass')
            else:
                if not self.client:
                    raise ScraperError('Client não inicializado')

                response = await self.client.get(url)
                response_text = response.text

                if response.status_code == 403:
                    raise BlockedError(f'Status 403 - Acesso bloqueado')

                if 'Digite o código:' in response_text:
                    raise CaptchaError('CAPTCHA detectado')

                if response.status_code != 200:
                    raise ScraperError(f'HTTP {response.status_code}')

            return response_text
        except httpx.RequestError as e:
            raise ScraperError(f'Erro de requisição: {str(e)}')
        except asyncio.TimeoutError:
            raise ScraperError('Timeout na requisição')

    async def fetch_page(self, url: str) -> html.HtmlElement:
        try:
            response_text = await self._fetch_with_retry(url)
            return html.fromstring(response_text)
        except Exception as e:
            self.logger.error(f'Falha ao obter página {url}: {str(e)}')
            raise