"""CrustAPI public LinkedIn data tool for LangChain."""

from typing import Any, Dict, Literal, Optional, Type

from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from langchain_crustapi._utilities import CrustAPILinkedInAPIWrapper


class CrustAPILinkedInInput(BaseModel):
    """Input for the CrustAPI LinkedIn tool."""

    url: Optional[str] = Field(
        default=None,
        description=(
            "A LinkedIn URL, like linkedin.com/in/satyanadella or "
            "linkedin.com/company/openai. Required for profile, company, "
            "and posts."
        ),
    )
    keywords: Optional[str] = Field(
        default=None,
        description=(
            "Search keywords, like 'python developer'. Required for people "
            "search, and for jobs when no job url is given."
        ),
    )


class CrustAPILinkedIn(BaseTool):  # type: ignore[override]
    """Get public LinkedIn data through CrustAPI as clean, structured JSON.

    One tool covers five LinkedIn surfaces via ``linkedin_type``: ``profile``
    (default), ``company``, ``posts``, ``jobs``, and ``search`` (people
    search). This is public, logged-out LinkedIn data only. You only pay for
    successful results, and there is a free tier with no card.

    Setup:
        Install ``langchain-crustapi`` and set the ``CRUSTAPI_API_KEY``
        environment variable with a key from https://crustapi.com.

        .. code-block:: bash

            pip install langchain-crustapi
            export CRUSTAPI_API_KEY="your-key"

    Instantiate:
        .. code-block:: python

            from langchain_crustapi import CrustAPILinkedIn

            tool = CrustAPILinkedIn()

    Invoke:
        .. code-block:: python

            tool.invoke({"url": "https://www.linkedin.com/in/satyanadella"})
    """

    name: str = "crustapi_linkedin"
    description: str = (
        "Get public LinkedIn data via CrustAPI as clean, structured JSON. "
        "Useful for a person's profile, a company page, recent posts, job "
        "listings, or people search. Input is a LinkedIn URL or search keywords."
    )
    args_schema: Type[BaseModel] = CrustAPILinkedInInput

    linkedin_type: Literal[
        "profile",
        "company",
        "posts",
        "jobs",
        "search",
    ] = "profile"
    """Which LinkedIn surface to query."""

    limit: Optional[int] = None
    """Maximum number of results (posts, jobs, or people). API defaults apply."""

    start: Optional[int] = None
    """Result offset for jobs (default 0)."""

    location: Optional[str] = None
    """Location filter for jobs, e.g. ``Austin, TX``."""

    enrich: bool = False
    """People search only: return each person's full profile in the same call."""

    employees: bool = False
    """Company only: include the employee list."""

    comments: bool = False
    """Posts only: include comments."""

    api_wrapper: CrustAPILinkedInAPIWrapper = Field(default_factory=CrustAPILinkedInAPIWrapper)  # type: ignore[arg-type]

    def __init__(self, **kwargs: Any) -> None:
        # Let callers pass crustapi_api_key / api_base_url straight through to the wrapper.
        if "api_wrapper" not in kwargs:
            wrapper_kwargs = {}
            if "crustapi_api_key" in kwargs:
                wrapper_kwargs["crustapi_api_key"] = kwargs.pop("crustapi_api_key")
            if "api_base_url" in kwargs:
                wrapper_kwargs["api_base_url"] = kwargs.pop("api_base_url")
            if wrapper_kwargs:
                kwargs["api_wrapper"] = CrustAPILinkedInAPIWrapper(**wrapper_kwargs)
        super().__init__(**kwargs)

    def _run(
        self,
        url: Optional[str] = None,
        keywords: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        """Fetch the LinkedIn data."""
        return self.api_wrapper.raw_results(
            linkedin_type=self.linkedin_type,
            url=url,
            keywords=keywords,
            location=self.location,
            start=self.start,
            limit=self.limit,
            enrich=self.enrich,
            employees=self.employees,
            comments=self.comments,
        )

    async def _arun(
        self,
        url: Optional[str] = None,
        keywords: Optional[str] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        """Fetch the LinkedIn data asynchronously."""
        return await self.api_wrapper.raw_results_async(
            linkedin_type=self.linkedin_type,
            url=url,
            keywords=keywords,
            location=self.location,
            start=self.start,
            limit=self.limit,
            enrich=self.enrich,
            employees=self.employees,
            comments=self.comments,
        )
