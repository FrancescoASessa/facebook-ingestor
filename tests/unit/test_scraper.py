import json
import pytest
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

from app.scraper import (
    extract_page_title,
    extract_about_via_js,
    scrape,
)
from app.reporting import ScrapeReport


@pytest.mark.asyncio
async def test_extract_page_title_valid():
    tab = MagicMock()
    tab.evaluate = AsyncMock(return_value="  My Page Title  ")

    result = await extract_page_title(tab)

    assert result == "My Page Title"
    tab.evaluate.assert_awaited_once_with("document.title")


@pytest.mark.asyncio
async def test_extract_page_title_empty_string():
    tab = MagicMock()
    tab.evaluate = AsyncMock(return_value="   ")

    result = await extract_page_title(tab)

    assert result is None


@pytest.mark.asyncio
async def test_extract_page_title_exception():
    tab = MagicMock()
    tab.evaluate = AsyncMock(side_effect=Exception("JS error"))

    result = await extract_page_title(tab)

    assert result is None


@pytest.mark.asyncio
async def test_extract_about_via_js_success():
    tab = MagicMock()
    tab.evaluate = AsyncMock(return_value='{"name": "Test"}')

    result = await extract_about_via_js(tab)

    assert result == '{"name": "Test"}'
    tab.evaluate.assert_awaited_once()


@pytest.mark.asyncio
async def test_extract_about_via_js_not_found():
    tab = MagicMock()
    tab.evaluate = AsyncMock(return_value=None)

    with pytest.raises(RuntimeError, match="about_app_sections not found"):
        await extract_about_via_js(tab)


@pytest.mark.asyncio
async def test_extract_about_via_js_invalid_type():
    tab = MagicMock()
    tab.evaluate = AsyncMock(return_value=123)

    with pytest.raises(RuntimeError, match="Expected JSON string"):
        await extract_about_via_js(tab)


@pytest.mark.asyncio
async def test_scrape_success(tmp_path):
    tab = MagicMock()
    tab.wait = AsyncMock()
    tab.target.url = "https://facebook.com/test-page"

    report = MagicMock(spec=ScrapeReport)
    report.record_saved = AsyncMock()
    report.record_failed = AsyncMock()

    with (
        patch("app.scraper.extract_page_title", AsyncMock(return_value="My Page")),
        patch(
            "app.scraper.extract_about_via_js",
            AsyncMock(return_value='{"key": "value"}'),
        ),
        patch("app.scraper.log_resources"),
        patch("app.scraper.safe_filename", return_value="test-page"),
        patch("builtins.open", mock_open()) as m_open,
    ):
        await scrape(tab, report)

    report.record_saved.assert_awaited_once()
    report.record_failed.assert_not_awaited()

    m_open.assert_called_once_with("data/test-page.json", "w", encoding="utf-8")


@pytest.mark.asyncio
async def test_scrape_invalid_json_payload():
    tab = MagicMock()
    tab.wait = AsyncMock()
    tab.target.url = "https://facebook.com/test-page"

    report = MagicMock(spec=ScrapeReport)
    report.record_saved = AsyncMock()
    report.record_failed = AsyncMock()

    with (
        patch("app.scraper.extract_page_title", AsyncMock(return_value="My Page")),
        patch("app.scraper.extract_about_via_js", AsyncMock(return_value="NOT JSON")),
        patch("app.scraper.log_resources"),
    ):
        await scrape(tab, report)

    report.record_failed.assert_awaited_once()
    report.record_saved.assert_not_awaited()
