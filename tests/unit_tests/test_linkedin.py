import os
from unittest.mock import MagicMock, patch

import pytest

from langchain_crustapi import CrustAPILinkedIn, CrustAPILinkedInAPIWrapper


@pytest.fixture(autouse=True)
def mock_api_key():
    with patch.dict(os.environ, {"CRUSTAPI_API_KEY": "test_key"}):
        yield


def test_tool_initialization():
    tool = CrustAPILinkedIn()
    assert tool.name == "crustapi_linkedin"
    assert tool.linkedin_type == "profile"
    assert tool.enrich is False


def test_wrapper_reads_env_key():
    wrapper = CrustAPILinkedInAPIWrapper()
    assert wrapper.crustapi_api_key.get_secret_value() == "test_key"


def test_wrapper_rejects_invalid_linkedin_type():
    wrapper = CrustAPILinkedInAPIWrapper()
    with pytest.raises(ValueError, match="Invalid linkedin_type"):
        wrapper.raw_results(linkedin_type="bogus")


def test_wrapper_requires_url_for_profile():
    wrapper = CrustAPILinkedInAPIWrapper()
    with pytest.raises(ValueError, match="requires a LinkedIn url"):
        wrapper.raw_results(linkedin_type="profile")


def test_wrapper_requires_keywords_for_search():
    wrapper = CrustAPILinkedInAPIWrapper()
    with pytest.raises(ValueError, match="requires keywords"):
        wrapper.raw_results(linkedin_type="search")


def test_wrapper_requires_keywords_or_url_for_jobs():
    wrapper = CrustAPILinkedInAPIWrapper()
    with pytest.raises(ValueError, match="keywords or a job url"):
        wrapper.raw_results(linkedin_type="jobs")


@patch("langchain_crustapi._utilities.requests.get")
def test_profile(mock_get):
    body = {
        "type": "linkedin-profile",
        "url": "https://www.linkedin.com/in/satyanadella",
        "profile": {"name": "Satya Nadella", "headline": "Chairman and CEO"},
    }
    mock_get.return_value = MagicMock(
        status_code=200, json=lambda: body, raise_for_status=lambda: None
    )
    tool = CrustAPILinkedIn()
    result = tool.invoke({"url": "https://www.linkedin.com/in/satyanadella"})
    assert result["profile"]["name"] == "Satya Nadella"
    # correct endpoint, params and auth header
    args, kw = mock_get.call_args
    assert args[0] == "https://crustapi.com/v1/linkedin"
    assert kw["params"]["type"] == "profile"
    assert kw["params"]["url"] == "https://www.linkedin.com/in/satyanadella"
    assert kw["headers"]["x-api-key"] == "test_key"


@patch("langchain_crustapi._utilities.requests.get")
def test_company_with_employees(mock_get):
    body = {
        "type": "linkedin-company",
        "company": {"name": "OpenAI", "employees": [{"name": "A"}]},
    }
    mock_get.return_value = MagicMock(
        status_code=200, json=lambda: body, raise_for_status=lambda: None
    )
    tool = CrustAPILinkedIn(linkedin_type="company", employees=True)
    result = tool.invoke({"url": "https://www.linkedin.com/company/openai"})
    assert result["company"]["name"] == "OpenAI"
    _, kw = mock_get.call_args
    assert kw["params"]["type"] == "company"
    assert kw["params"]["employees"] == "true"


@patch("langchain_crustapi._utilities.requests.get")
def test_jobs_with_keywords_and_location(mock_get):
    body = {"type": "linkedin-jobs", "jobs": [{"title": "Python Developer"}]}
    mock_get.return_value = MagicMock(
        status_code=200, json=lambda: body, raise_for_status=lambda: None
    )
    tool = CrustAPILinkedIn(linkedin_type="jobs", location="Austin, TX", limit=10)
    result = tool.invoke({"keywords": "python developer"})
    assert result["jobs"][0]["title"] == "Python Developer"
    _, kw = mock_get.call_args
    assert kw["params"]["type"] == "jobs"
    assert kw["params"]["keywords"] == "python developer"
    assert kw["params"]["location"] == "Austin, TX"
    assert kw["params"]["limit"] == 10


@patch("langchain_crustapi._utilities.requests.get")
def test_people_search_with_enrich(mock_get):
    body = {"type": "linkedin-search", "people": [{"name": "Jane Doe"}]}
    mock_get.return_value = MagicMock(
        status_code=200, json=lambda: body, raise_for_status=lambda: None
    )
    tool = CrustAPILinkedIn(linkedin_type="search", enrich=True)
    result = tool.invoke({"keywords": "growth marketer saas"})
    assert result["people"][0]["name"] == "Jane Doe"
    _, kw = mock_get.call_args
    assert kw["params"]["type"] == "search"
    assert kw["params"]["enrich"] == "true"


@patch("langchain_crustapi._utilities.requests.get")
def test_posts_with_comments(mock_get):
    body = {"type": "linkedin-posts", "posts": [{"text": "hello"}]}
    mock_get.return_value = MagicMock(
        status_code=200, json=lambda: body, raise_for_status=lambda: None
    )
    tool = CrustAPILinkedIn(linkedin_type="posts", comments=True)
    result = tool.invoke({"url": "https://www.linkedin.com/in/satyanadella"})
    assert result["posts"][0]["text"] == "hello"
    _, kw = mock_get.call_args
    assert kw["params"]["type"] == "posts"
    assert kw["params"]["comments"] == "true"
