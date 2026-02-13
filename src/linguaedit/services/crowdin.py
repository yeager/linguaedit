"""Crowdin API v2 client for fetching projects, progress, and managing translations."""
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
import urllib.request
import urllib.error
from typing import Optional

BASE = "https://api.crowdin.com/api/v2"


class CrowdinError(Exception):
    pass


def _request(endpoint: str, api_key: str, method: str = "GET",
             params: Optional[dict] = None, body: Optional[dict] = None,
             raw_body: Optional[bytes] = None,
             extra_headers: Optional[dict] = None,
             base_url: str = BASE) -> dict | bytes:
    """Make a request to Crowdin API v2."""
    url = f"{base_url}{endpoint}"
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{qs}"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    if extra_headers:
        headers.update(extra_headers)

    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    elif raw_body is not None:
        data = raw_body

    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
            ct = resp.headers.get("Content-Type", "")
            if "json" in ct:
                return json.loads(content.decode())
            return content
    except urllib.error.HTTPError as e:
        body_text = e.read().decode() if e.fp else ""
        raise CrowdinError(f"HTTP {e.code}: {body_text[:500]}") from e
    except Exception as e:
        raise CrowdinError(str(e)) from e


def _paginate(endpoint: str, api_key: str, params: Optional[dict] = None,
              base_url: str = BASE) -> list:
    """Fetch all pages from a paginated Crowdin endpoint."""
    results = []
    offset = 0
    limit = 25
    p = dict(params) if params else {}
    p["limit"] = limit
    while True:
        p["offset"] = offset
        data = _request(endpoint, api_key, params=p, base_url=base_url)
        items = data.get("data", [])
        results.extend(items)
        if len(items) < limit:
            break
        offset += limit
    return results


def fetch_projects(api_key: str, base_url: str = BASE) -> list[dict]:
    """Return list of {id, name, identifier, source_language, target_languages}."""
    items = _paginate("/projects", api_key, {"hasManagerAccess": "0"}, base_url=base_url)
    return [
        {
            "id": it["data"]["id"],
            "name": it["data"].get("name", ""),
            "identifier": it["data"].get("identifier", ""),
            "source_language": it["data"].get("sourceLanguageId", ""),
            "target_languages": [
                lang.get("id", "") for lang in it["data"].get("targetLanguages", [])
            ],
        }
        for it in items
    ]


def fetch_project_details(api_key: str, project_id: int, base_url: str = BASE) -> dict:
    """Return project details: name, sourceLanguageId, targetLanguages."""
    data = _request(f"/projects/{project_id}", api_key, base_url=base_url)
    d = data.get("data", {})
    return {
        "id": d.get("id"),
        "name": d.get("name", ""),
        "identifier": d.get("identifier", ""),
        "source_language": d.get("sourceLanguageId", ""),
        "target_languages": d.get("targetLanguages", []),
    }


def fetch_project_progress(api_key: str, project_id: int, base_url: str = BASE) -> list[dict]:
    """Return per-language progress: [{language, phrases, translated, approved, pct_translated, pct_approved}]."""
    items = _paginate(f"/projects/{project_id}/languages/progress", api_key, base_url=base_url)
    result = []
    for it in items:
        d = it.get("data", {})
        lang_id = d.get("languageId", "")
        phrases = d.get("phrases", {}).get("total", 0)
        translated = d.get("phrases", {}).get("translated", 0)
        approved = d.get("phrases", {}).get("approved", 0)
        pct_t = d.get("translationProgress", 0)
        pct_a = d.get("approvalProgress", 0)
        result.append({
            "language": lang_id,
            "phrases": phrases,
            "translated": translated,
            "approved": approved,
            "pct_translated": pct_t,
            "pct_approved": pct_a,
        })
    return sorted(result, key=lambda x: x["language"])


def fetch_files(api_key: str, project_id: int, base_url: str = BASE) -> list[dict]:
    """Return list of source files: [{id, name, title, type}]."""
    items = _paginate(f"/projects/{project_id}/files", api_key, base_url=base_url)
    return [
        {
            "id": it["data"]["id"],
            "name": it["data"].get("name", ""),
            "title": it["data"].get("title", ""),
            "type": it["data"].get("type", ""),
        }
        for it in items
    ]


def fetch_file_progress(api_key: str, project_id: int, file_id: int,
                        base_url: str = BASE) -> list[dict]:
    """Return per-language progress for a specific file."""
    items = _paginate(
        f"/projects/{project_id}/files/{file_id}/languages/progress",
        api_key, base_url=base_url,
    )
    result = []
    for it in items:
        d = it.get("data", {})
        result.append({
            "language": d.get("languageId", ""),
            "phrases": d.get("phrases", {}).get("total", 0),
            "translated": d.get("phrases", {}).get("translated", 0),
            "approved": d.get("phrases", {}).get("approved", 0),
            "pct_translated": d.get("translationProgress", 0),
            "pct_approved": d.get("approvalProgress", 0),
        })
    return sorted(result, key=lambda x: x["language"])


def fetch_languages(api_key: str, base_url: str = BASE) -> list[dict]:
    """Return Crowdin supported languages."""
    items = _paginate("/languages", api_key, base_url=base_url)
    return [
        {
            "id": it["data"]["id"],
            "name": it["data"].get("name", ""),
            "locale": it["data"].get("locale", ""),
        }
        for it in items
    ]


def build_translations(api_key: str, project_id: int, base_url: str = BASE) -> int:
    """Trigger a translation build. Returns build ID."""
    data = _request(
        f"/projects/{project_id}/translations/builds", api_key,
        method="POST", body={}, base_url=base_url,
    )
    return data.get("data", {}).get("id", 0)


def get_build_status(api_key: str, project_id: int, build_id: int,
                     base_url: str = BASE) -> dict:
    """Check build status. Returns {status, progress}."""
    data = _request(
        f"/projects/{project_id}/translations/builds/{build_id}",
        api_key, base_url=base_url,
    )
    d = data.get("data", {})
    return {"status": d.get("status", ""), "progress": d.get("progress", 0)}


def get_build_download_url(api_key: str, project_id: int, build_id: int,
                           base_url: str = BASE) -> str:
    """Get download URL for a completed build."""
    data = _request(
        f"/projects/{project_id}/translations/builds/{build_id}/download",
        api_key, base_url=base_url,
    )
    return data.get("data", {}).get("url", "")


def upload_to_storage(api_key: str, filename: str, content: bytes,
                      base_url: str = BASE) -> int:
    """Upload file to Crowdin storage. Returns storage ID."""
    data = _request(
        "/storages", api_key, method="POST",
        raw_body=content,
        extra_headers={
            "Crowdin-API-FileName": filename,
            "Content-Type": "application/octet-stream",
        },
        base_url=base_url,
    )
    return data.get("data", {}).get("id", 0)


def add_file(api_key: str, project_id: int, storage_id: int, name: str,
             base_url: str = BASE) -> dict:
    """Add a source file to project from storage."""
    data = _request(
        f"/projects/{project_id}/files", api_key, method="POST",
        body={"storageId": storage_id, "name": name},
        base_url=base_url,
    )
    return data.get("data", {})


def upload_translation(api_key: str, project_id: int, language_id: str,
                       storage_id: int, file_id: int,
                       base_url: str = BASE) -> dict:
    """Upload a translation file for a specific language."""
    data = _request(
        f"/projects/{project_id}/translations/{language_id}", api_key,
        method="POST",
        body={"storageId": storage_id, "fileId": file_id},
        base_url=base_url,
    )
    return data.get("data", {})
