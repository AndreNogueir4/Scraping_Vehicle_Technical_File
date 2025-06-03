class ScraperError(Exception):
    pass

class BlockedError(ScraperError):
    pass

class CaptchaError(ScraperError):
    pass

class RetryableError(ScraperError):
    pass