import pytest
from unittest.mock import AsyncMock, MagicMock

from app.cookies import (
    wait_cookie_banner,
    click_element,
    find_cookie_button,
    fast_accept_cookies,
)


@pytest.mark.asyncio
async def test_wait_cookie_banner_found():
    tab = MagicMock()
    element = MagicMock()
    tab.find = AsyncMock(return_value=element)

    result = await wait_cookie_banner(tab)

    assert result is element
    tab.find.assert_awaited_once_with("cookie", best_match=True, timeout=15)


@pytest.mark.asyncio
async def test_wait_cookie_banner_not_found():
    tab = MagicMock()
    tab.find = AsyncMock(side_effect=Exception("not found"))

    result = await wait_cookie_banner(tab)

    assert result is None
    tab.find.assert_awaited_once()


@pytest.mark.asyncio
async def test_click_element_executes_actions_in_order():
    tab = MagicMock()
    tab.wait = AsyncMock()

    el = MagicMock()
    el.scroll_into_view = AsyncMock()
    el.click = AsyncMock()

    await click_element(tab, el)

    el.scroll_into_view.assert_awaited_once()
    el.click.assert_awaited_once()

    # Due attese: 0.3 e 1
    assert tab.wait.await_count == 2
    tab.wait.assert_any_await(0.3)
    tab.wait.assert_any_await(1)


@pytest.mark.asyncio
async def test_find_cookie_button_first_label_found():
    tab = MagicMock()
    element = MagicMock()

    tab.find = AsyncMock(side_effect=[element])

    result = await find_cookie_button(tab)

    assert result is element
    tab.find.assert_awaited_once()


@pytest.mark.asyncio
async def test_find_cookie_button_second_label_found():
    tab = MagicMock()
    element = MagicMock()

    tab.find = AsyncMock(side_effect=[None, element])

    result = await find_cookie_button(tab)

    assert result is element
    assert tab.find.await_count == 2


@pytest.mark.asyncio
async def test_find_cookie_button_not_found():
    tab = MagicMock()
    tab.find = AsyncMock(return_value=None)

    result = await find_cookie_button(tab)

    assert result is None
    assert tab.find.await_count == 2


@pytest.mark.asyncio
async def test_fast_accept_cookies_clicks_and_waits_when_found():
    tab = MagicMock()
    tab.evaluate = AsyncMock(return_value="Consenti solo i cookie essenziali")
    tab.wait = AsyncMock()

    await fast_accept_cookies(tab)

    tab.evaluate.assert_awaited_once()
    tab.wait.assert_awaited_once_with(0.5)


@pytest.mark.asyncio
async def test_fast_accept_cookies_noop_when_not_found():
    tab = MagicMock()
    tab.evaluate = AsyncMock(return_value=None)
    tab.wait = AsyncMock()

    await fast_accept_cookies(tab)

    tab.evaluate.assert_awaited_once()
    tab.wait.assert_not_awaited()
