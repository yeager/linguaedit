"""Weblate API client for fetching projects, components, and translation statistics.

Weblate is self-hosted, so a base URL is required in addition to the API token.
Authentication uses ``Authorization: Token {key}``.

API reference: https://docs.weblate.org/en/latest/api.html

SPDX-License-Identifier: GPL-3.0-or-later
"""

from __future__ import annotations

import json
import urllib.request
import urllib.error
from typing import Optional


class WeblateError(Exception):
    pass


def _request(
    base_url: str,
    endpoint: str,
    api_key: str,
    *,
    method: str = "GET",
    data: bytes | None = None,
    content_type: str = "application/json",
    accept: str = "application/json",
    timeout: int = 30,
    raw: bool = False,
) -> dict | bytes:
    """Make a request to the Weblate API.

    *base_url* – e.g. ``https://weblate.example.com``
    *endpoint* – e.g. ``/api/projects/``
    """
    url = f"{base_url.rstrip('/')}{endpoint}"
    headers = {
        "Authorization": f"Token {api_key}",
        "Accept": accept,
    }
    if data is not None:
        headers["Content-Type"] = content_type

    req = urllib.request.Request(url, headers=headers, method=method, data=data)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            if raw:
                return body
            return json.loads(body.decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:500] if e.fp else ""
        raise WeblateError(f"HTTP {e.code}: {detail}") from e
    except Exception as e:
        raise WeblateError(str(e)) from e


def _paginate(base_url: str, endpoint: str, api_key: str) -> list:
    """Fetch all pages from a paginated Weblate endpoint."""
    results: list = []
    data = _request(base_url, endpoint, api_key)
    results.extend(data.get("results", []))
    while data.get("next"):
        next_url = data["next"]
        # next is a full URL – make it relative
        suffix = next_url.replace(base_url.rstrip("/"), "")
        data = _request(base_url, suffix, api_key)
        results.extend(data.get("results", []))
    return results


# ── Public helpers ────────────────────────────────────────────────────


def fetch_projects(base_url: str, api_key: str) -> list[dict]:
    """Return list of ``{slug, name, web}``."""
    items = _paginate(base_url, "/api/projects/", api_key)
    return [
        {
            "slug": it["slug"],
            "name": it["name"],
            "web": it.get("web", ""),
        }
        for it in items
    ]


def fetch_components(base_url: str, api_key: str, project_slug: str) -> list[dict]:
    """Return list of ``{slug, name, vcs, repo}`` for a project."""
    items = _paginate(base_url, f"/api/projects/{project_slug}/components/", api_key)
    return [
        {
            "slug": it["slug"],
            "name": it["name"],
            "vcs": it.get("vcs", ""),
            "repo": it.get("repo", ""),
        }
        for it in items
    ]


def fetch_component_statistics(
    base_url: str, api_key: str, project_slug: str, component_slug: str,
) -> list[dict]:
    """Return per-language statistics for a component.

    Each item: ``{language, translated, fuzzy, total, pct}``.
    """
    items = _paginate(
        base_url,
        f"/api/components/{project_slug}/{component_slug}/statistics/",
        api_key,
    )
    # The endpoint may return a single object (not paginated) with a "results" key
    # OR a flat list already handled by _paginate.
    # Weblate >= 4.x returns {"count": N, "results": [...]} or a flat dict per language.
    # Normalise:
    if not items:
        # Try non-paginated (the endpoint returns a flat list keyed by language)
        data = _request(base_url, f"/api/components/{project_slug}/{component_slug}/statistics/", api_key)
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict) and "results" in data:
            items = data["results"]
        else:
            items = [data]

    result = []
    for it in items:
        lang = it.get("language", it.get("code", "?"))
        total = it.get("total", 0)
        translated = it.get("translated", 0)
        fuzzy = it.get("fuzzy", 0)
        pct = it.get("translated_percent", 0.0)
        if total and not pct:
            pct = round(translated / total * 100, 1)
        result.append({
            "language": lang,
            "translated": translated,
            "fuzzy": fuzzy,
            "total": total,
            "pct": round(pct, 1),
        })
    return sorted(result, key=lambda x: x["language"])


def fetch_project_statistics(base_url: str, api_key: str, project_slug: str) -> list[dict]:
    """Return aggregated per-language stats across all components in a project.

    Uses ``GET /api/projects/{project}/statistics/``.
    """
    data = _request(base_url, f"/api/projects/{project_slug}/statistics/", api_key)
    # This endpoint returns a flat list of per-language stats
    items = data if isinstance(data, list) else data.get("results", [data])
    result = []
    for it in items:
        lang = it.get("language", it.get("code", "?"))
        total = it.get("total", 0)
        translated = it.get("translated", 0)
        fuzzy = it.get("fuzzy", 0)
        pct = it.get("translated_percent", 0.0)
        if total and not pct:
            pct = round(translated / total * 100, 1)
        result.append({
            "language": lang,
            "translated": translated,
            "fuzzy": fuzzy,
            "total": total,
            "pct": round(pct, 1),
        })
    return sorted(result, key=lambda x: x["language"])


def fetch_translations(
    base_url: str, api_key: str, project_slug: str, component_slug: str,
) -> list[dict]:
    """Return list of translations for a component: ``{language_code, filename, translated, total}``."""
    items = _paginate(
        base_url,
        f"/api/components/{project_slug}/{component_slug}/translations/",
        api_key,
    )
    return [
        {
            "language_code": it.get("language", {}).get("code", it.get("language_code", "?")),
            "filename": it.get("filename", ""),
            "translated": it.get("translated", 0),
            "total": it.get("total", 0),
        }
        for it in items
    ]


def fetch_languages(base_url: str, api_key: str) -> list[dict]:
    """Return all languages known to this Weblate instance."""
    items = _paginate(base_url, "/api/languages/", api_key)
    return [
        {"code": it["code"], "name": it.get("name", it["code"])}
        for it in items
    ]


def download_translation(
    base_url: str, api_key: str,
    project_slug: str, component_slug: str, language_code: str,
) -> bytes:
    """Download a translation file (PO, XLIFF, etc.) as raw bytes."""
    return _request(
        base_url,
        f"/api/translations/{project_slug}/{component_slug}/{language_code}/file/",
        api_key,
        raw=True,
    )


def upload_translation(
    base_url: str, api_key: str,
    project_slug: str, component_slug: str, language_code: str,
    file_content: bytes, filename: str = "upload.po",
    method_param: str = "translate",
) -> dict:
    """Upload a translation file.

    *method_param* can be ``translate``, ``suggest``, ``approve``, etc.
    Uses multipart/form-data.
    """
    import uuid

    boundary = uuid.uuid4().hex
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode() + file_content + (
        f"\r\n--{boundary}\r\n"
        f'Content-Disposition: form-data; name="method"\r\n\r\n'
        f"{method_param}\r\n"
        f"--{boundary}--\r\n"
    ).encode()

    return _request(
        base_url,
        f"/api/translations/{project_slug}/{component_slug}/{language_code}/file/",
        api_key,
        method="POST",
        data=body,
        content_type=f"multipart/form-data; boundary={boundary}",
    )


def trigger_pull(base_url: str, api_key: str, project_slug: str, component_slug: str) -> dict:
    """Trigger VCS pull for a component."""
    return _request(
        base_url,
        f"/api/components/{project_slug}/{component_slug}/repository/",
        api_key,
        method="POST",
        data=json.dumps({"operation": "pull"}).encode(),
    )


def trigger_push(base_url: str, api_key: str, project_slug: str, component_slug: str) -> dict:
    """Trigger VCS push for a component."""
    return _request(
        base_url,
        f"/api/components/{project_slug}/{component_slug}/repository/",
        api_key,
        method="POST",
        data=json.dumps({"operation": "push"}).encode(),
    )
