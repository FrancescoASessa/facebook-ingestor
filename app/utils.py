"""Shared utility functions for URL handling, validation, and batching."""

import json
import re
from urllib.parse import urlparse, urlunparse


def chunked(lst, n):
    """Yield successive chunks from a list.

    This generator splits a list into consecutive sublists of a given
    size. The final chunk may be smaller if the list length is not
    evenly divisible by the chunk size.

    Args:
        lst (list): The list to be split into chunks.
        n (int): The maximum size of each chunk.

    Yields:
        list: A sublist containing up to `n` elements.
    """
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def safe_filename(url: str) -> str:
    """Generate a filesystem-safe filename from a URL.

    This function converts the path component of a URL into a sanitized
    filename by replacing path separators, removing unsafe characters,
    and ensuring a non-empty result.

    Args:
        url (str): The URL from which to derive the filename.

    Returns:
        str: A filesystem-safe filename derived from the URL path.
    """
    path = urlparse(url).path.strip("/").replace("/", "_")
    path = re.sub(r"[^a-zA-Z0-9_-]", "", path)
    return path or "index"


def is_json_string(value) -> bool:
    """Check whether a value is a valid JSON-formatted string.

    This function attempts to parse the given value as JSON. Only
    string values are considered valid candidates.

    Args:
        value (Any): The value to validate.

    Returns:
        bool: True if the value is a valid JSON string, False otherwise.
    """
    if not isinstance(value, str):
        return False
    try:
        json.loads(value)
        return True
    except json.JSONDecodeError:
        return False


def ensure_about(url: str) -> str:
    """Ensure that a Facebook URL points to the `/about` section.

    If the provided URL does not already end with `/about`, this
    function appends `/about` while preserving the rest of the URL
    structure.

    Args:
        url (str): The original Facebook page URL.

    Returns:
        str: The normalized URL pointing to the `/about` section.
    """

    parsed = urlparse(url)
    path = parsed.path or "/"

    normalized = path.rstrip("/")

    if normalized.endswith("/about"):
        return url

    if path.endswith("/"):
        path = path + "about"
    else:
        path = path + "/about"

    return urlunparse(parsed._replace(path=path))
