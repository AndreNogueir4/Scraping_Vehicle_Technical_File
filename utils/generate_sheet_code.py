import random

async def generate_unique_sheet_code(check_exists_fn):
    while True:
        code = ''.join(random.choices('0123456789', k=5))
        exists = await check_exists_fn(code)
        if not exists:
            return code