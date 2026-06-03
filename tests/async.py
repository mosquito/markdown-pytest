import asyncio

import pytest


@pytest.fixture
async def async_fixture():
    await asyncio.sleep(0)
    return asyncio.get_event_loop()
