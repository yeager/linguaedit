"""Transifex API v3 client for fetching organizations, projects, and stats."""

from __future__ import annotations

import json
import urllib.request
import urllib.error
from typing import Optional

BASE = "https://rest.api.transifex.com"


class TransifexError(Exception):
    pass


def _request(endpoint: str, api_key: str, params: Optional[dict] = None) -> dict:
    """Make a GET request to Transifex API v3."""
    url = f"{BASE}{endpoint}"
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{qs}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/vnd.api+json",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        raise TransifexError(f"HTTP {e.code}: {body[:500]}") from e
    except Exception as e:
        raise TransifexError(str(e)) from e


def _paginate(endpoint: str, api_key: str, params: Optional[dict] = None) -> list:
    """Fetch all pages from a paginated endpoint."""
    results = []
    data = _request(endpoint, api_key, params)
    results.extend(data.get("data", []))
    while data.get("links", {}).get("next"):
        next_url = data["links"]["next"]
        # next is a full URL, strip base
        suffix = next_url.replace(BASE, "")
        req = urllib.request.Request(next_url, headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/vnd.api+json",
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        results.extend(data.get("data", []))
    return results


def fetch_organizations(api_key: str) -> list[dict]:
    """Return list of {id, slug, name}."""
    items = _paginate("/organizations", api_key)
    return [
        {
            "id": it["id"],
            "slug": it["attributes"]["slug"],
            "name": it["attributes"]["name"],
        }
        for it in items
    ]


def fetch_projects(api_key: str, org_slug: str) -> list[dict]:
    """Return list of {id, slug, name} for an organization."""
    items = _paginate("/projects", api_key, {
        "filter[organization]": f"o:{org_slug}",
    })
    return [
        {
            "id": it["id"],
            "slug": it["attributes"]["slug"],
            "name": it["attributes"]["name"],
        }
        for it in items
    ]


def fetch_project_stats(api_key: str, org_slug: str, project_slug: str) -> list[dict]:
    """Return per-language stats: [{language, translated, reviewed, total, pct}]."""
    items = _paginate("/resource_language_stats", api_key, {
        "filter[project]": f"o:{org_slug}:p:{project_slug}",
    })
    # Aggregate across resources per language
    lang_map: dict[str, dict] = {}
    for it in items:
        attrs = it.get("attributes", {})
        # language id is in relationships
        lang_id = it.get("relationships", {}).get("language", {}).get("data", {}).get("id", "")
        # lang_id like "l:sv" → "sv"
        lang_code = lang_id.split(":")[-1] if ":" in lang_id else lang_id

        if lang_code not in lang_map:
            lang_map[lang_code] = {"language": lang_code, "translated": 0, "reviewed": 0, "total": 0}

        lang_map[lang_code]["translated"] += attrs.get("translated_strings", 0)
        lang_map[lang_code]["reviewed"] += attrs.get("reviewed_strings", 0)
        lang_map[lang_code]["total"] += attrs.get("total_strings", 0)

    result = []
    for info in sorted(lang_map.values(), key=lambda x: x["language"]):
        total = info["total"]
        info["pct"] = round(info["translated"] / total * 100, 1) if total else 0.0
        result.append(info)
    return result
