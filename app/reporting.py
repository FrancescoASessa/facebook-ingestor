"""Execution reporting and aggregation utilities for scraping jobs."""

import asyncio

from app.observability import get_logger

logger = get_logger(__name__)


class ScrapeReport:
    """Aggregate and report scraping results across concurrent workers.

    This class provides an asyncio-safe mechanism to track how many
    scraping operations succeeded or failed during a run and to emit
    a final summary report once execution completes.
    """

    def __init__(self):
        """Initialize an empty scrape report."""

        self._saved = 0
        self._failed = 0
        self._lock = asyncio.Lock()

    async def record_saved(self):
        """Record a successful scrape result."""

        async with self._lock:
            self._saved += 1

    async def record_failed(self):
        """Record a failed scrape result."""

        async with self._lock:
            self._failed += 1

    def summary(self) -> dict:
        """Return a summary of scraping results.

        Returns:
            dict: A dictionary containing total, saved, and failed counts.
        """
        return {
            "saved": self._saved,
            "failed": self._failed,
            "total": self._saved + self._failed,
        }

    def log_summary(self):
        """Log the final scraping summary."""

        summary = self.summary()
        logger.info(
            "Scraping completed. Total=%d, Saved=%d, Failed=%d",
            summary["total"],
            summary["saved"],
            summary["failed"],
        )
