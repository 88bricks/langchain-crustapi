from importlib import metadata
from typing import List

from langchain_crustapi.crustapi_linkedin import CrustAPILinkedIn
from langchain_crustapi.crustapi_search import CrustAPISearch
from langchain_crustapi._utilities import (
    CrustAPILinkedInAPIWrapper,
    CrustAPISearchAPIWrapper,
)

try:
    __version__: str = metadata.version(__package__)
except metadata.PackageNotFoundError:
    __version__ = ""
del metadata

__all__: List[str] = [
    "CrustAPILinkedIn",
    "CrustAPILinkedInAPIWrapper",
    "CrustAPISearch",
    "CrustAPISearchAPIWrapper",
    "__version__",
]
