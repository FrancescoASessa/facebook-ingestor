import asyncio
import pytest

from app.reporting import ScrapeReport


@pytest.mark.asyncio
async def test_scrape_report_initial_state():
    report = ScrapeReport()
    summary = report.summary()

    assert summary == {"saved": 0, "failed": 0, "total": 0}


@pytest.mark.asyncio
async def test_scrape_report_saved_and_failed():
    report = ScrapeReport()

    await report.record_saved()
    await report.record_failed()
    await report.record_saved()

    summary = report.summary()

    assert summary["saved"] == 2
    assert summary["failed"] == 1
    assert summary["total"] == 3


@pytest.mark.asyncio
async def test_summary_invariant():
    report = ScrapeReport()

    await report.record_saved()
    await report.record_failed()
    await report.record_failed()

    summary = report.summary()

    assert summary["total"] == summary["saved"] + summary["failed"]


@pytest.mark.asyncio
async def test_summary_is_pure_function():
    report = ScrapeReport()

    await report.record_saved()
    before = report.summary()

    after = report.summary()

    assert before == after


@pytest.mark.asyncio
async def test_concurrent_updates():
    report = ScrapeReport()

    async def worker():
        await report.record_saved()
        await report.record_failed()

    tasks = [worker() for _ in range(50)]
    await asyncio.gather(*tasks)

    summary = report.summary()

    assert summary["saved"] == 50
    assert summary["failed"] == 50
    assert summary["total"] == 100


@pytest.mark.asyncio
async def test_only_saved():
    report = ScrapeReport()

    for _ in range(5):
        await report.record_saved()

    summary = report.summary()

    assert summary == {"saved": 5, "failed": 0, "total": 5}


@pytest.mark.asyncio
async def test_only_failed():
    report = ScrapeReport()

    for _ in range(3):
        await report.record_failed()

    summary = report.summary()

    assert summary == {"saved": 0, "failed": 3, "total": 3}


@pytest.mark.asyncio
async def test_log_summary_does_not_crash(caplog):
    report = ScrapeReport()

    await report.record_saved()
    await report.record_failed()

    with caplog.at_level("INFO"):
        report.log_summary()

    assert "Scraping completed" in caplog.text
