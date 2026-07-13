"""CrustAPI Google search tool for LangChain."""

from typing import Any, Dict, Literal, Optional, Type

from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from langchain_crustapi._utilities import CrustAPISearchAPIWrapper


class CrustAPISearchInput(BaseModel):
    """Input for the CrustAPI search tool."""

    query: str = Field(description="Search query to look up on Google")


class CrustAPISearch(BaseTool):  # type: ignore[override]
    """Search Google through CrustAPI and get clean, structured JSON.

    One tool covers multiple Google surfaces via ``search_type``: ``web``
    (default), ``news``, ``maps``, ``places``, ``shopping``, ``images``,
    ``videos``, ``scholar``, and ``patents``. You only pay for successful
    results, and there is a free tier with no card.

    Setup:
        Install ``langchain-crustapi`` and set the ``CRUSTAPI_API_KEY``
        environment variable with a key from https://crustapi.com.

        .. code-block:: bash

            pip install langchain-crustapi
            export CRUSTAPI_API_KEY="your-key"

    Instantiate:
        .. code-block:: python

            from langchain_crustapi import CrustAPISearch

            tool = CrustAPISearch(max_results=5)

    Invoke:
        .. code-block:: python

            tool.invoke({"query": "best crm software"})
    """

    name: str = "crustapi_search"
    description: str = (
        "Search Google via CrustAPI and return clean, structured JSON. "
        "Useful for current web results, local businesses (maps), news, "
        "shopping, images, videos, scholar, and patents. Input is a search query."
    )
    args_schema: Type[BaseModel] = CrustAPISearchInput

    search_type: Literal[
        "web",
        "news",
        "maps",
        "places",
        "shopping",
        "images",
        "videos",
        "scholar",
        "patents",
    ] = "web"
    """Which Google surface to query."""

    max_results: int = 10
    """Maximum number of results to return."""

    gl: Optional[str] = None
    """Two-letter country code, e.g. ``us``."""

    hl: Optional[str] = None
    """Two-letter language code, e.g. ``en``."""

    location: Optional[str] = None
    """City or region for local results, e.g. ``Austin, TX``."""

    api_wrapper: CrustAPISearchAPIWrapper = Field(default_factory=CrustAPISearchAPIWrapper)  # type: ignore[arg-type]

    def __init__(self, **kwargs: Any) -> None:
        # Let callers pass crustapi_api_key / api_base_url straight through to the wrapper.
        if "api_wrapper" not in kwargs:
            wrapper_kwargs = {}
            if "crustapi_api_key" in kwargs:
                wrapper_kwargs["crustapi_api_key"] = kwargs.pop("crustapi_api_key")
            if "api_base_url" in kwargs:
                wrapper_kwargs["api_base_url"] = kwargs.pop("api_base_url")
            if wrapper_kwargs:
                kwargs["api_wrapper"] = CrustAPISearchAPIWrapper(**wrapper_kwargs)
        super().__init__(**kwargs)

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        """Run the search."""
        return self.api_wrapper.raw_results(
            query=query,
            search_type=self.search_type,
            num=self.max_results,
            gl=self.gl,
            hl=self.hl,
            location=self.location,
        )

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        """Run the search asynchronously."""
        return await self.api_wrapper.raw_results_async(
            query=query,
            search_type=self.search_type,
            num=self.max_results,
            gl=self.gl,
            hl=self.hl,
            location=self.location,
        )
