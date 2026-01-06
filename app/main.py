"""Command-line interface entrypoint for the Facebook Ingestor application."""

import asyncio
import logging

import click

from app.observability import Observability
from app.orchestrator import run_parallel


async def run_async(urls: list[str], browsers: int):
    """Execute the asynchronous scraping workflow.

    This coroutine acts as a bridge between the synchronous Click
    command-line interface and the asynchronous scraping logic.
    It delegates execution to the parallel orchestrator.

    Args:
        urls (list[str]): List of target URLs to scrape.
        browsers (int): Number of parallel browser instances to launch.
    """
    await run_parallel(urls, browsers)


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--browsers",
    "-b",
    default=10,
    show_default=True,
    type=int,
    help="Number of parallel browser instances to launch.",
)
@click.option(
    "--urls-file",
    "-f",
    type=click.Path(exists=True, dir_okay=False),
    required=True,
    help="Path to a text file containing one URL per line.",
)
@click.option(
    "--log-resources/--no-log-resources",
    default=True,
    show_default=True,
    help="Enable or disable hardware resource logging.",
)
def cli(browsers: int, urls_file: str, log_resources: bool):
    """Run the Facebook scraper using a Click-based CLI.

    This command initializes application-wide logging, loads target URLs
    from a file, and starts the asynchronous scraping workflow using the
    specified level of parallelism.

    The command is designed for production and batch execution
    environments.
    """

    Observability.setup(
        level=logging.INFO,
        enable_resource_logging=log_resources,
    )

    with open(urls_file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    if not urls:
        raise click.ClickException("No valid URLs found in the provided file.")

    asyncio.run(run_async(urls, browsers))


# pylint: disable=no-value-for-parameter
if __name__ == "__main__":
    cli()
