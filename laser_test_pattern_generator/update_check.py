from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Mapping, Optional


LATEST_RELEASE_API_URL = "https://api.github.com/repos/wdani/laser-test-pattern-generator/releases/latest"
LATEST_RELEASE_PAGE_URL = "https://github.com/wdani/laser-test-pattern-generator/releases/latest"
DEFAULT_UPDATE_TIMEOUT_SECONDS = 5.0
DEFAULT_UPDATE_CHECK_ON_STARTUP = False

_VERSION_RE = re.compile(r"^[vV]?(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:[-+][0-9A-Za-z.-]+)?$")


@dataclass(frozen=True)
class ReleaseInfo:
    tag_name: str
    version: str
    html_url: str


@dataclass(frozen=True)
class UpdateCheckResult:
    current_version: str
    latest_version: Optional[str]
    latest_tag: Optional[str]
    release_url: str
    is_update_available: bool
    error: Optional[str] = None


def default_update_preferences() -> dict:
    return {
        "update_check_on_startup": DEFAULT_UPDATE_CHECK_ON_STARTUP,
        "update_last_checked": "",
        "update_snooze_until": "",
        "update_ignored_version": "",
    }


def normalize_version_tag(tag: object) -> Optional[str]:
    if not isinstance(tag, str):
        return None

    match = _VERSION_RE.match(tag.strip())
    if not match:
        return None

    major = int(match.group(1))
    minor = int(match.group(2) or 0)
    patch = int(match.group(3) or 0)
    return f"{major}.{minor}.{patch}"


def version_tuple(tag: object) -> Optional[tuple[int, int, int]]:
    normalized = normalize_version_tag(tag)
    if normalized is None:
        return None
    major, minor, patch = normalized.split(".")
    return int(major), int(minor), int(patch)


def compare_versions(current_version: object, latest_version: object) -> Optional[int]:
    """Compare latest against current.

    Returns 1 if latest is newer, 0 if equal, -1 if latest is older, or None
    when either version cannot be parsed.
    """
    current = version_tuple(current_version)
    latest = version_tuple(latest_version)
    if current is None or latest is None:
        return None
    if latest > current:
        return 1
    if latest < current:
        return -1
    return 0


def _response_to_dict(response: object) -> dict:
    if isinstance(response, bytes):
        response = response.decode("utf-8")
    if isinstance(response, str):
        response = json.loads(response)
    if not isinstance(response, dict):
        raise ValueError("latest release response must be a JSON object")
    return response


def parse_latest_release_response(response: object) -> ReleaseInfo:
    data = _response_to_dict(response)
    tag_name = data.get("tag_name")
    html_url = data.get("html_url")

    if not isinstance(tag_name, str) or not tag_name.strip():
        raise ValueError("latest release response is missing tag_name")

    version = normalize_version_tag(tag_name)
    if version is None:
        raise ValueError(f"latest release tag is not a supported version: {tag_name}")

    if not isinstance(html_url, str) or not html_url.startswith("https://"):
        raise ValueError("latest release response is missing html_url")

    return ReleaseInfo(tag_name=tag_name.strip(), version=version, html_url=html_url.strip())


def fetch_latest_release(timeout: float = DEFAULT_UPDATE_TIMEOUT_SECONDS) -> ReleaseInfo:
    request = urllib.request.Request(
        LATEST_RELEASE_API_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Laser-Test-Pattern-Generator",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return parse_latest_release_response(response.read())


def check_for_update(current_version: str, timeout: float = DEFAULT_UPDATE_TIMEOUT_SECONDS) -> UpdateCheckResult:
    try:
        release = fetch_latest_release(timeout=timeout)
    except (OSError, urllib.error.URLError, json.JSONDecodeError, ValueError) as exc:
        return UpdateCheckResult(
            current_version=current_version,
            latest_version=None,
            latest_tag=None,
            release_url=LATEST_RELEASE_PAGE_URL,
            is_update_available=False,
            error=str(exc),
        )

    comparison = compare_versions(current_version, release.tag_name)
    return UpdateCheckResult(
        current_version=current_version,
        latest_version=release.version,
        latest_tag=release.tag_name,
        release_url=release.html_url,
        is_update_available=comparison == 1,
        error=None if comparison is not None else f"could not compare versions: {current_version} and {release.tag_name}",
    )


def date_from_value(value: object) -> Optional[date]:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str) and value.strip():
        try:
            return date.fromisoformat(value.strip()[:10])
        except ValueError:
            return None
    return None


def today_from_value(value: object = None) -> date:
    parsed = date_from_value(value)
    return parsed if parsed is not None else date.today()


def date_text(value: object = None) -> str:
    return today_from_value(value).isoformat()


def snooze_until(days: int, today: object = None) -> str:
    return (today_from_value(today) + timedelta(days=int(days))).isoformat()


def is_ignored_version(latest_version: object, preferences: Mapping[str, object]) -> bool:
    latest = normalize_version_tag(latest_version)
    ignored = normalize_version_tag(preferences.get("update_ignored_version"))
    return latest is not None and ignored is not None and latest == ignored


def should_check_for_updates(preferences: Mapping[str, object], today: object = None) -> bool:
    if not bool(preferences.get("update_check_on_startup", DEFAULT_UPDATE_CHECK_ON_STARTUP)):
        return False

    current_day = today_from_value(today)
    snoozed_until = date_from_value(preferences.get("update_snooze_until"))
    if snoozed_until is not None and snoozed_until > current_day:
        return False

    last_checked = date_from_value(preferences.get("update_last_checked"))
    if last_checked is not None and last_checked >= current_day:
        return False

    return True


def should_notify_update(result: UpdateCheckResult, preferences: Mapping[str, object]) -> bool:
    if result.error or not result.is_update_available:
        return False
    return not is_ignored_version(result.latest_tag or result.latest_version, preferences)

