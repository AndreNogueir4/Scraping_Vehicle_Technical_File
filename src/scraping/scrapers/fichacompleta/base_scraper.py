import httpx
import asyncio
import os
import random
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from lxml import html
from fake_useragent import UserAgent
from logger import get_logger
from ..shared.exceptions import ScraperError, BlockedError, CaptchaError, RetryableError

class BaseScraper:
    BASE_URL = 'https://www.fichacompleta.com.br'
    REFERENCE = 'fichacompleta'
    DEFAULT_TIMEOUT = 30.0
    MAX_RETRIES = 5
    RETRY_DELAYS = [1, 3, 5, 10, 15]

    def __init__(self):
        load_dotenv()
        self.logger = get_logger(self.__class__.__name__, reference=self.REFERENCE)
        self.client = None
        self._proxies = os.getenv('PROXIES', '').split(',') if os.getenv('PROXIES') else []
        self._current_proxy = None
        self._user_agent = UserAgent()

    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            headers=self._generate_headers(),
            timeout=self.DEFAULT_TIMEOUT,
            follow_redirects=True,
            http2=True
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
            self.client = None

    def _generate_headers(self, referer: str = None) -> Dict[str, str]:
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;"
                      "q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "max-age=0",
            "priority": "u=0, i",
            "referer": referer or f"{self.BASE_URL}/carros/",
            "sec-ch-ua": '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": self._user_agent.random,
        }
        return headers

    async def _fetch_with_retry(self, url: str, max_retries: int = None) -> str:
        max_retries = max_retries or self.MAX_RETRIES

        for attempt in range(max_retries):
            try:
                response_text = await self._try_fetch(url, attempt)
                return response_text
            except (BlockedError, CaptchaError, RetryableError) as e:
                self.logger.warning(f"Tentativa {attempt + 1}/{max_retries} falhou: {str(e)}")
                if attempt == max_retries - 1:
                    raise ScraperError(f"Falha após {max_retries} tentativas: {str(e)}")

                delay = self.RETRY_DELAYS[min(attempt, len(self.RETRY_DELAYS) - 1)]
                jitter = random.uniform(0.5, 1.5)
                await asyncio.sleep(delay * jitter)

    async def _try_fetch(self, url: str, attempt: int) -> str:
        try:
            use_proxy = attempt > 0 and self._proxies
            if use_proxy:
                proxy = random.choice(self._proxies)
                self.logger.info(f"Tentando com proxy: {proxy}")

                async with httpx.AsyncClient(
                        headers=self._generate_headers(url),
                        proxies={"http://": proxy, "https://": proxy},
                        timeout=self.DEFAULT_TIMEOUT
                ) as proxy_client:
                    response = await proxy_client.get(url)
                    response_text = response.text

                    if response.status_code != 200:
                        raise RetryableError(f"Proxy retornou status {response.status_code}")

                    if 'Digite o código:' in response_text:
                        raise CaptchaError("CAPTCHA detectado mesmo com proxy")

                    return response_text
            else:
                if not self.client:
                    raise ScraperError("Client HTTP não inicializado")

                response = await self.client.get(url)
                response_text = response.text

                if response.status_code == 403:
                    raise BlockedError("Acesso bloqueado (403)")

                if response.status_code == 429:
                    raise RetryableError("Rate limit atingido (429)")

                if 'Digite o código:' in response_text:
                    raise CaptchaError("CAPTCHA detectado na resposta")

                if response.status_code != 200:
                    raise RetryableError(f"Status HTTP {response.status_code}")

                return response_text

        except httpx.ConnectError as e:
            raise RetryableError(f"Erro de conexão: {str(e)}")
        except httpx.ReadTimeout:
            raise RetryableError("Timeout na leitura da resposta")
        except httpx.RequestError as e:
            raise RetryableError(f"Erro na requisição: {str(e)}")