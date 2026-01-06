import pytest
from unittest.mock import AsyncMock, MagicMock

from app.browser_setup import (
    build_browser_config,
    set_mobile_emulation,
    enable_network_optimizations,
)


def test_build_browser_config_without_suffix():
    config = build_browser_config()

    assert config.headless is True
    assert config.user_data_dir == "./chrome-profile-fb"
    assert "--disable-background-networking" in config.args
    assert "--disable-extensions" in config.args


def test_build_browser_config_with_suffix():
    config = build_browser_config("worker-1")

    assert config.user_data_dir == "./chrome-profile-fb-worker-1"


@pytest.mark.asyncio
async def test_set_mobile_emulation_sends_two_commands():
    tab = MagicMock()
    tab.send = AsyncMock()

    await set_mobile_emulation(tab)

    # Deve inviare due comandi CDP
    assert tab.send.await_count == 2

    first_call = tab.send.await_args_list[0]
    second_call = tab.send.await_args_list[1]

    # Verifica che siano comandi CDP (non None)
    assert first_call.args[0] is not None
    assert second_call.args[0] is not None


@pytest.mark.asyncio
async def test_enable_network_optimizations_sends_commands():
    tab = MagicMock()
    tab.send = AsyncMock()

    await enable_network_optimizations(tab)

    # enable + set_blocked_urls
    assert tab.send.await_count == 2

    calls = tab.send.await_args_list

    assert calls[0].args[0] is not None
    assert calls[1].args[0] is not None
