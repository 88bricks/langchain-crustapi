"""Utility wrapper for the CrustAPI Google search endpoint."""

from typing import Any, Dict, Optional

import aiohttp
import requests
from langchain_core.utils import get_from_dict_or_env
from pydantic import BaseModel, ConfigDict, SecretStr, model_validator

CRUSTAPI_URL = "https://crustapi.com/v1/search"

# Google surfaces CrustAPI exposes through the single search endpoint.
SEARCH_TYPES = (
    "web",
    "news",
    "maps",
    "places",
    "shopping",
    "images",
    "videos",
    "scholar",
    "patents",
)


class CrustAPISearchAPIWrapper(BaseModel):
    """Wrapper around the CrustAPI search endpoint.

    Reads the API key from the ``crustapi_api_key`` argument or the
    ``CRUSTAPI_API_KEY`` environment variable. Get a free key at
    https://crustapi.com (3,000 credits per month, no card).
    """

    crustapi_api_key: SecretStr
    api_base_url: Optional[str] = None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: Dict) -> Any:
        """Validate that the API key exists in the arguments or environment."""
        values["crustapi_api_key"] = get_from_dict_or_env(
            values, "crustapi_api_key", "CRUSTAPI_API_KEY"
        )
        return values

    def _build_params(
        self,
        query: str,
        search_type: str,
        num: int,
        gl: Optional[str],
        hl: Optional[str],
        location: Optional[str],
    ) -> Dict[str, Any]:
        if search_type not in SEARCH_TYPES:
            raise ValueError(
                f"Invalid search_type: {search_type}. "
                f"Must be one of: {', '.join(SEARCH_TYPES)}"
            )
        params: Dict[str, Any] = {"type": search_type, "q": query, "num": num}
        if gl:
            params["gl"] = gl
        if hl:
            params["hl"] = hl
        if location:
            params["location"] = location
        return params

    def raw_results(
        self,
        query: str,
        search_type: str = "web",
        num: int = 10,
        gl: Optional[str] = None,
        hl: Optional[str] = None,
        location: Optional[str] = None,
    ) -> Dict:
        """Run a search and return the raw JSON response."""
        params = self._build_params(query, search_type, num, gl, hl, location)
        headers = {"x-api-key": self.crustapi_api_key.get_secret_value()}
        base_url = self.api_base_url or CRUSTAPI_URL
        response = requests.get(base_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()

    async def raw_results_async(
        self,
        query: str,
        search_type: str = "web",
        num: int = 10,
        gl: Optional[str] = None,
        hl: Optional[str] = None,
        location: Optional[str] = None,
    ) -> Dict:
        """Run a search asynchronously and return the raw JSON response."""
        params = self._build_params(query, search_type, num, gl, hl, location)
        headers = {"x-api-key": self.crustapi_api_key.get_secret_value()}
        base_url = self.api_base_url or CRUSTAPI_URL
        async with aiohttp.ClientSession() as session:
            async with session.get(
                base_url,
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                response.raise_for_status()
                return await response.json()
