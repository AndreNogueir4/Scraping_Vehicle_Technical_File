import pytest
from utils.generate_sheet_code import generate_unique_sheet_code

@pytest.mark.asyncio
async def test_generate_unique_sheet_code_return_5_digit_code():
    async def fake_check_exists_fn():
        return False

    code = await generate_unique_sheet_code(fake_check_exists_fn)

    assert isinstance(code, str)
    assert len(code) == 5
    assert code.isdigit()