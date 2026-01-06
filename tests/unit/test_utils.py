import pytest

from app.utils import (
    chunked,
    ensure_about,
    is_json_string,
    safe_filename,
)


def test_chunked_exact():
    data = [1, 2, 3, 4]
    chunks = list(chunked(data, 2))
    assert chunks == [[1, 2], [3, 4]]


def test_chunked_remainder():
    data = [1, 2, 3]
    chunks = list(chunked(data, 2))
    assert chunks == [[1, 2], [3]]


def test_safe_filename_normal_path():
    url = "https://facebook.com/foo/bar"
    assert safe_filename(url) == "foo_bar"


def test_safe_filename_root_path():
    url = "https://facebook.com/"
    assert safe_filename(url) == "index"


def test_safe_filename_strips_invalid_chars():
    url = "https://facebook.com/foo/@@@bar!!!"
    assert safe_filename(url) == "foo_bar"


def test_is_json_string_valid():
    assert is_json_string('{"a": 1}')
    assert is_json_string('["a", "b"]')


def test_is_json_string_invalid():
    assert not is_json_string("{bad json}")
    assert not is_json_string(123)
    assert not is_json_string(None)


def test_ensure_about_adds_suffix():
    url = "https://facebook.com/page"
    assert ensure_about(url) == "https://facebook.com/page/about"


def test_ensure_about_idempotent():
    url = "https://facebook.com/page/about"
    assert ensure_about(url) == url


def test_ensure_about_trailing_slash():
    url = "https://facebook.com/page/about/"
    assert ensure_about(url) == url


def test_ensure_about_path_with_trailing_slash():
    url = "https://facebook.com/page/"
    assert ensure_about(url) == "https://facebook.com/page/about"
