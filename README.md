# langchain-crustapi

This package connects [CrustAPI](https://crustapi.com) to LangChain, giving your chains and agents clean, structured Google data from one endpoint: web search, Maps, News, Shopping, Images, Videos, Places, Scholar, and Patents. You only pay for successful results, and there's a free tier with no card.

## Installation

```bash
pip install -U langchain-crustapi
export CRUSTAPI_API_KEY="your-key"   # free at https://crustapi.com
```

## Usage

```python
from langchain_crustapi import CrustAPISearch

# Web search (default)
tool = CrustAPISearch(max_results=5)
tool.invoke({"query": "best crm software"})

# Pick a Google surface
maps = CrustAPISearch(search_type="maps", location="Austin, TX")
maps.invoke({"query": "dentists"})

news = CrustAPISearch(search_type="news")
news.invoke({"query": "openai"})
```

Bind it to an agent like any other LangChain tool:

```python
from langchain.chat_models import init_chat_model
from langchain_crustapi import CrustAPISearch

llm = init_chat_model("gpt-4o-mini")
agent_llm = llm.bind_tools([CrustAPISearch()])
```

## Parameters

- `search_type`: the Google surface — `web` (default), `news`, `maps`, `places`, `shopping`, `images`, `videos`, `scholar`, `patents`.
- `max_results`: number of results to return (default `10`).
- `gl`: two-letter country code, e.g. `us`.
- `hl`: two-letter language code, e.g. `en`.
- `location`: city or region for local results, e.g. `Austin, TX`.

The API key is read from the `CRUSTAPI_API_KEY` environment variable, or you can pass `crustapi_api_key` when constructing the tool.
