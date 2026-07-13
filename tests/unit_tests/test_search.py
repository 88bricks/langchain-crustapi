import os
from unittest.mock import MagicMock, patch

import pytest

from langchain_crustapi import CrustAPISearch, CrustAPISearchAPIWrapper


@pytest.fixture(autouse=True)
def mock_api_key():
    with patch.dict(os.environ, {"CRUSTAPI_API_KEY": "test_key"}):
        yield


def test_tool_initialization():
    tool = CrustAPISearch()
    assert tool.name == "crustapi_search"
    assert tool.search_type == "web"
    assert tool.max_results == 10


def test_wrapper_reads_env_key():
    wrapper = CrustAPISearchAPIWrapper()
    assert wrapper.crustapi_api_key.get_secret_value() == "test_key"


def test_wrapper_rejects_invalid_search_type():
    wrapper = CrustAPISearchAPIWrapper()
    with pytest.raises(ValueError, match="Invalid search_type"):
        wrapper.raw_results("q", search_type="bogus")


@patch("langchain_crustapi._utilities.requests.get")
def test_web_search(mock_get):
    body = {
        "searchParameters": {"q": "q", "type": "web"},
        "organic": [{"title": "T1", "link": "l1", "snippet": "s", "position": 1}],
    }
    mock_get.return_value = MagicMock(
        status_code=200, json=lambda: body, raise_for_status=lambda: None
    )
    tool = CrustAPISearch(max_results=2)
    result = tool.invoke({"query": "q"})
    assert result["organic"][0]["title"] == "T1"
    # correct endpoint, params and auth header
    _, kw = mock_get.call_args
    assert kw["params"]["type"] == "web"
    assert kw["params"]["q"] == "q"
    assert kw["headers"]["x-api-key"] == "test_key"


@patch("langchain_crustapi._utilities.requests.get")
def test_maps_search_type(mock_get):
    body = {"searchParameters": {"q": "c", "type": "maps"}, "places": [{"title": "Cafe"}]}
    mock_get.return_value = MagicMock(
        status_code=200, json=lambda: body, raise_for_status=lambda: None
    )
    tool = CrustAPISearch(search_type="maps")
    result = tool.invoke({"query": "c"})
    assert result["places"][0]["title"] == "Cafe"
    _, kw = mock_get.call_args
    assert kw["params"]["type"] == "maps"
