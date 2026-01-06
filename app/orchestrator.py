"""Parallel orchestration logic for browser-based scraping workers."""

import asyncio
from typing import List

from nodriver import start

from app.browser_setup import (
    build_browser_config,
    enable_network_optimizations,
    set_mobile_emulation,
)
from app.cookies import fast_accept_cookies
from app.observability import get_logger, log_resources
from app.performance import Timer
from app.reporting import ScrapeReport
from app.scraper import scrape
from app.utils import chunked, ensure_about

logger = get_logger(__name__)


async def browser_worker(worker_id: int, urls: List[str], report: ScrapeReport):
    """Run a single browser worker to scrape a subset of URLs.

    Each worker launches an isolated browser instance with its own
    profile, applies standard network and mobile emulation settings,
    and sequentially processes a list of URLs. Cookie handling is
    performed once per worker to minimize overhead.

    Args:
        worker_id (int): Unique identifier for the worker, used for
            logging and browser profile isolation.
        urls (List[str]): List of URLs assigned to this worker.
    """
    logger.info(
        "Worker %d starting execution (assigned_urls=%d)",
        worker_id,
        len(urls),
    )

    config = build_browser_config(str(worker_id))
    t = Timer()
    browser = await start(config)

    logger.info(
        "Browser instance started for worker %d (startup_time=%.2fs)",
        worker_id,
        t.lap(),
    )
    log_resources(f"worker {worker_id} after browser startup")

    tab = await browser.get("about:blank")
    await enable_network_optimizations(tab)
    await set_mobile_emulation(tab)

    cookie_done = False

    for i, url in enumerate(urls, start=1):
        await tab.get(ensure_about(url))

        if not cookie_done:
            await fast_accept_cookies(tab)
            cookie_done = True

        await scrape(tab, report)

        if i % 10 == 0:
            log_resources(f"worker {worker_id} after processing {i} urls")

    logger.info(
        "Worker %d completed execution successfully",
        worker_id,
    )
    browser.stop()


async def run_parallel(urls: List[str], browsers: int):
    """Execute multiple browser workers in parallel.

    This function splits the input URL list into evenly sized chunks
    and assigns each chunk to a dedicated browser worker. All workers
    are executed concurrently using asyncio.

    Args:
        urls (List[str]): Complete list of URLs to be scraped.
        browsers (int): Number of parallel browser instances to launch.
    """
    report = ScrapeReport()
    chunks = list(chunked(urls, (len(urls) + browsers - 1) // browsers))

    logger.info(
        "Starting parallel execution (total_urls=%d, browsers=%d, urls_per_browser≈%d)",
        len(urls),
        browsers,
        len(chunks[0]),
    )

    tasks = [browser_worker(i + 1, chunk, report) for i, chunk in enumerate(chunks)]

    await asyncio.gather(*tasks)
    report.log_summary()
