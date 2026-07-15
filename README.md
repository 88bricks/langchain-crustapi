# langchain-crustapi

This package connects [CrustAPI](https://crustapi.com) to LangChain, giving your chains and agents clean, structured Google data from one endpoint (web search, Maps, News, Shopping, Images, Videos, Places, Scholar, and Patents) plus public LinkedIn data (profiles, companies, posts, jobs, and people search). You only pay for successful results, and there's a free tier with no card.

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

## LinkedIn tool

`CrustAPILinkedIn` returns public LinkedIn data as the same clean JSON: a person's profile, a company page, recent posts, job listings, or people search. Pick the surface with `linkedin_type` and pass a LinkedIn URL or keywords.

```python
from langchain_crustapi import CrustAPILinkedIn

# Profile (default)
profile = CrustAPILinkedIn()
profile.invoke({"url": "https://www.linkedin.com/in/satyanadella"})

# People search, with each person's full profile in the same call
people = CrustAPILinkedIn(linkedin_type="search", enrich=True)
people.invoke({"keywords": "growth marketer saas"})
```

## Parameters

### CrustAPISearch

- `search_type`: the Google surface, `web` (default), `news`, `maps`, `places`, `shopping`, `images`, `videos`, `scholar`, `patents`.
- `max_results`: number of results to return (default `10`).
- `gl`: two-letter country code, e.g. `us`.
- `hl`: two-letter language code, e.g. `en`.
- `location`: city or region for local results, e.g. `Austin, TX`.

### CrustAPILinkedIn

- `linkedin_type`: `profile` (default), `company`, `posts`, `jobs`, `search`.
- `limit`: max results for posts, jobs, or people search.
- `start`: result offset for jobs.
- `location`: location filter for jobs, e.g. `Austin, TX`.
- `enrich`: people search only, return each person's full profile in the same call.
- `employees`: company only, include the employee list.
- `comments`: posts only, include comments.

`profile`, `company`, and `posts` take a `url`. `search` takes `keywords`. `jobs` takes `keywords` (plus optional `location`) or a job `url`.

The API key is read from the `CRUSTAPI_API_KEY` environment variable, or you can pass `crustapi_api_key` when constructing either tool.
