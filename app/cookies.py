"""Cookie consent handling utilities for browser-based scraping."""

from typing import Union

from nodriver import Element, Tab

from app.observability import get_logger

logger = get_logger(__name__)


async def wait_cookie_banner(tab: Tab, timeout: int = 15) -> Union[Element, None]:
    """Wait for a cookie consent banner to appear on the page.

    This function attempts to locate a cookie-related element on the page
    within a given timeout. It is intended as a slower, fallback mechanism
    when fast JavaScript-based cookie handling is not sufficient.

    Args:
        tab (Tab): The Nodriver tab instance to search within.
        timeout (int): Maximum time in seconds to wait for the cookie
            banner to appear.

    Returns:
        Element | None: The detected cookie banner element if found,
        otherwise None.
    """
    try:
        el = await tab.find("cookie", best_match=True, timeout=timeout)
        logger.info("Cookie banner trovato")
        return el
    except Exception:
        logger.info("Cookie banner NON trovato")
        return None


async def click_element(tab: Tab, el: Element):
    """Scroll an element into view and perform a click action.

    This helper ensures that the element is visible before clicking,
    introducing small delays to reduce the risk of interaction failures
    caused by layout shifts or asynchronous rendering.

    Args:
        tab (Tab): The Nodriver tab instance associated with the element.
        el (Element): The element to be clicked.
    """
    await el.scroll_into_view()
    await tab.wait(0.3)
    await el.click()
    await tab.wait(1)


async def find_cookie_button(tab: Tab) -> Union[Element, None]:
    """Find a cookie consent button using predefined Italian labels.

    The function searches for commonly used Italian cookie consent
    button labels related to rejecting optional cookies or accepting
    only essential cookies.

    Args:
        tab (Tab): The Nodriver tab instance to search within.

    Returns:
        Element | None: The matching cookie button element if found,
        otherwise None.
    """
    for text in (
        "Rifiuta cookie facoltativi",
        "Consenti solo i cookie essenziali",
    ):
        btn = await tab.find(text, best_match=True, timeout=3)
        if btn:
            return btn
    return None


async def fast_accept_cookies(tab: Tab):
    """Attempt to accept or reject cookies using a fast JavaScript strategy.

    This function executes an in-page JavaScript snippet that directly
    searches for cookie consent buttons by their `aria-label` attributes
    and clicks them if found. This approach avoids DOM traversal via the
    automation API and is optimized for speed.

    Args:
        tab (Tab): The Nodriver tab instance where the script is executed.
    """
    logger.info("Trying fast cookie accept")

    js = r"""
    (() => {
      const labels = [
        "Consenti solo i cookie essenziali",
        "Rifiuta cookie facoltativi"
      ];

      for (const label of labels) {
        const btn = document.querySelector(
          `[aria-label="${label}"]`
        );
        if (btn) {
          btn.click();
          return label;
        }
      }
      return null;
    })();
    """

    result = await tab.evaluate(js, return_by_value=True)

    if result:
        logger.info("Cookie clicked via JS: %s", result)
        await tab.wait(0.5)
    else:
        logger.info("No cookie banner detected (fast path)")
