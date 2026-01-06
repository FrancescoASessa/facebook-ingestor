"""Page scraping and data extraction logic for Facebook business pages."""

import json
from typing import Optional

from nodriver import Tab

from app.observability import get_logger, log_resources
from app.performance import Timer
from app.reporting import ScrapeReport
from app.utils import is_json_string, safe_filename

logger = get_logger(__name__)


async def extract_page_title(tab: Tab) -> Optional[str]:
    """Extract the document title from the current page.

    This function retrieves the value of `document.title` via JavaScript
    execution. If the title cannot be extracted or an error occurs,
    the function returns `None` and logs a warning.

    Args:
        tab (Tab): The Nodriver tab instance representing the current page.

    Returns:
        Optional[str]: The page title if available, otherwise None.
    """
    try:
        result = await tab.evaluate("document.title")
        if isinstance(result, str) and result.strip():
            return result.strip()
    except Exception as e:
        logger.warning("Unable to extract <title>: %s", e)
    return None


async def extract_about_via_js(tab: Tab) -> str:
    """Extract business "About" information using in-page JavaScript.

    This function executes a JavaScript snippet that scans embedded
    JSON blobs within the page, recursively searching for the
    `about_app_sections` structure. The extracted data is normalized
    and returned as a JSON-formatted string.

    Args:
        tab (Tab): The Nodriver tab instance from which data is extracted.

    Returns:
        str: A JSON-formatted string containing the extracted business
        information.

    Raises:
        RuntimeError: If the expected `about_app_sections` data cannot
        be found within the page.
    """
    logger.info("Extracting About payload via in-page JS")

    js = r"""
    (() => {
      const scripts = Array.from(
        document.querySelectorAll('script[type="application/json"]')
      ).filter(s => s.textContent.includes("about_app_sections"));

      const blobs = scripts
        .map(s => {
          try { return JSON.parse(s.textContent); }
          catch { return null; }
        })
        .filter(Boolean);

      function deepFindAbout(node) {
        if (!node || typeof node !== 'object') return null;
        if (node.about_app_sections?.nodes) return node.about_app_sections;

        for (const key in node) {
          const v = node[key];
          if (!v || typeof v !== 'object') continue;
          const found = deepFindAbout(v);
          if (found) return found;
        }
        return null;
      }

      const about = blobs.map(deepFindAbout).find(Boolean);
      if (!about) return null;

      const result = {};
      for (const section of about.nodes || []) {
        for (const collection of section.activeCollections?.nodes || []) {
          const renderer = collection.style_renderer;
          if (!renderer) continue;

          for (const fieldSection of renderer.profile_field_sections || []) {
            for (const field of fieldSection.profile_fields?.nodes || []) {
              const type = field.field_type;
              const value = field.title?.text;
              if (type && value) result[type] = value;

              if (type === 'address' && field.map_pin_coordinates) {
                result.latitude = field.map_pin_coordinates.latitude;
                result.longitude = field.map_pin_coordinates.longitude;
              }
            }
          }
        }
      }
      return JSON.stringify(result);
    })();
    """

    data = await tab.evaluate(js, return_by_value=True)
    if not data:
        raise RuntimeError("about_app_sections not found via JS")

    if not isinstance(data, str):
        raise RuntimeError("Expected JSON string from JS evaluation")

    logger.info("Business data extracted successfully")
    return data


async def scrape(tab: Tab, report: ScrapeReport):
    """Scrape business information from the current page and persist it.

    This function orchestrates the scraping process for a single page:
    it waits for the DOM to stabilize, extracts the page title and
    business "About" data, validates the extracted payload, and writes
    the resulting data to a JSON file on disk.

    Args:
        tab (Tab): The Nodriver tab instance currently loaded with the
            target page.
    """
    await tab.wait(4)
    logger.info("DOM ready, skipping full HTML dump")

    t = Timer()
    title = await extract_page_title(tab)
    data = await extract_about_via_js(tab)
    log_resources("after about extraction")

    if not is_json_string(data):
        logger.warning("About payload non è JSON valido: %r", data)
        await report.record_failed()
        return

    logger.info("About extraction: %.3fs", t.lap())

    filename = f"data/{safe_filename(tab.target.url)}.json"
    payload = json.loads(data)
    payload["display_name"] = title

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    await report.record_saved()

    logger.info("Saved output to %s", filename)
    logger.info("Scraping completed successfully")
