"""Integration stubs for Transifex, Weblate, and Crowdin."""

from __future__ import annotations

import requests
from dataclasses import dataclass
from typing import Optional


class PlatformError(Exception):
    pass


# --- Transifex ---

@dataclass
class TransifexConfig:
    api_token: str
    organization: str
    project: str
    base_url: str = "https://rest.api.transifex.com"

    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/vnd.api+json",
        }


def transifex_list_resources(config: TransifexConfig) -> list[dict]:
    """List resources in a Transifex project."""
    url = f"{config.base_url}/resources"
    params = {"filter[project]": f"o:{config.organization}:p:{config.project}"}
    r = requests.get(url, headers=config.headers, params=params, timeout=30)
    if r.status_code != 200:
        raise PlatformError(f"Transifex: {r.status_code} {r.text}")
    return r.json().get("data", [])


def transifex_download(config: TransifexConfig, resource_id: str, language: str) -> str:
    """Download a translation file from Transifex."""
    url = f"{config.base_url}/resource_translations_async_downloads"
    payload = {
        "data": {
            "attributes": {"content_encoding": "text"},
            "relationships": {
                "resource": {"data": {"type": "resources", "id": resource_id}},
                "language": {"data": {"type": "languages", "id": f"l:{language}"}},
            },
            "type": "resource_translations_async_downloads",
        }
    }
    r = requests.post(url, headers=config.headers, json=payload, timeout=30)
    if r.status_code not in (200, 201, 202):
        raise PlatformError(f"Transifex download failed: {r.status_code}")
    # In reality, poll the redirect URL; simplified here
    return r.text


# --- Weblate ---

@dataclass
class WeblateConfig:
    api_url: str  # e.g. https://hosted.weblate.org/api/
    api_key: str
    project: str
    component: str

    @property
    def headers(self) -> dict:
        return {"Authorization": f"Token {self.api_key}"}


def weblate_list_translations(config: WeblateConfig) -> list[dict]:
    """List translations for a Weblate component."""
    url = f"{config.api_url}components/{config.project}/{config.component}/translations/"
    r = requests.get(url, headers=config.headers, timeout=30)
    if r.status_code != 200:
        raise PlatformError(f"Weblate: {r.status_code} {r.text}")
    return r.json().get("results", [])


def weblate_download(config: WeblateConfig, language: str) -> bytes:
    """Download a translation file from Weblate."""
    url = f"{config.api_url}translations/{config.project}/{config.component}/{language}/file/"
    r = requests.get(url, headers=config.headers, timeout=30)
    if r.status_code != 200:
        raise PlatformError(f"Weblate download failed: {r.status_code}")
    return r.content


def weblate_upload(config: WeblateConfig, language: str, file_content: bytes,
                   filename: str = "translation.po") -> dict:
    """Upload a translation file to Weblate."""
    url = f"{config.api_url}translations/{config.project}/{config.component}/{language}/file/"
    files = {"file": (filename, file_content)}
    r = requests.post(url, headers=config.headers, files=files, timeout=60)
    if r.status_code not in (200, 201):
        raise PlatformError(f"Weblate upload failed: {r.status_code}")
    return r.json()


# --- Crowdin ---

@dataclass
class CrowdinConfig:
    api_token: str
    project_id: int
    base_url: str = "https://api.crowdin.com/api/v2"

    @property
    def headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_token}"}


def crowdin_list_files(config: CrowdinConfig) -> list[dict]:
    """List files in a Crowdin project."""
    url = f"{config.base_url}/projects/{config.project_id}/files"
    r = requests.get(url, headers=config.headers, timeout=30)
    if r.status_code != 200:
        raise PlatformError(f"Crowdin: {r.status_code} {r.text}")
    return r.json().get("data", [])


def crowdin_download_build(config: CrowdinConfig, build_id: int) -> str:
    """Get download URL for a Crowdin build."""
    url = f"{config.base_url}/projects/{config.project_id}/translations/builds/{build_id}/download"
    r = requests.get(url, headers=config.headers, timeout=30)
    if r.status_code != 200:
        raise PlatformError(f"Crowdin download failed: {r.status_code}")
    return r.json().get("data", {}).get("url", "")
