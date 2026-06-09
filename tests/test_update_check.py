from datetime import date

import pytest

from laser_test_pattern_generator.update_check import (
    UpdateCheckResult,
    compare_versions,
    default_update_preferences,
    is_ignored_version,
    normalize_version_tag,
    parse_latest_release_response,
    should_check_for_updates,
    should_notify_update,
    snooze_until,
)


def test_compare_same_version():
    assert compare_versions("v1.6.2", "1.6.2") == 0


def test_compare_newer_version():
    assert compare_versions("v1.6.2", "v1.6.3") == 1


def test_compare_older_version():
    assert compare_versions("v1.6.2", "v1.6.1") == -1


def test_v_prefix_handling():
    assert normalize_version_tag("v1.6.2") == "1.6.2"
    assert normalize_version_tag("V1.6.2") == "1.6.2"
    assert normalize_version_tag("1.6.2") == "1.6.2"


def test_invalid_version_handling():
    assert normalize_version_tag("not-a-version") is None
    assert compare_versions("v1.6.2", "not-a-version") is None
    assert compare_versions("not-a-version", "v1.6.3") is None


def test_parse_latest_release_response():
    release = parse_latest_release_response(
        {
            "tag_name": "v1.6.3",
            "html_url": "https://github.com/wdani/laser-test-pattern-generator/releases/tag/v1.6.3",
        }
    )

    assert release.tag_name == "v1.6.3"
    assert release.version == "1.6.3"
    assert release.html_url.endswith("/v1.6.3")


def test_parse_latest_release_response_rejects_invalid_payload():
    with pytest.raises(ValueError):
        parse_latest_release_response({"name": "v1.6.3"})


def test_ignored_version_detection():
    prefs = default_update_preferences()
    prefs["update_ignored_version"] = "1.6.3"

    assert is_ignored_version("v1.6.3", prefs)
    assert not is_ignored_version("v1.6.4", prefs)


def test_should_notify_update_respects_ignored_version():
    prefs = default_update_preferences()
    prefs["update_ignored_version"] = "v1.6.3"
    result = UpdateCheckResult(
        current_version="v1.6.2",
        latest_version="1.6.3",
        latest_tag="v1.6.3",
        release_url="https://github.com/wdani/laser-test-pattern-generator/releases/tag/v1.6.3",
        is_update_available=True,
    )

    assert not should_notify_update(result, prefs)


def test_startup_check_disabled_by_default():
    prefs = default_update_preferences()

    assert prefs["update_check_on_startup"] is False
    assert not should_check_for_updates(prefs, date(2026, 6, 9))


def test_check_is_due_when_enabled_and_not_checked_today():
    prefs = default_update_preferences()
    prefs["update_check_on_startup"] = True
    prefs["update_last_checked"] = "2026-06-08"

    assert should_check_for_updates(prefs, date(2026, 6, 9))


def test_check_is_not_due_after_checking_today():
    prefs = default_update_preferences()
    prefs["update_check_on_startup"] = True
    prefs["update_last_checked"] = "2026-06-09"

    assert not should_check_for_updates(prefs, date(2026, 6, 9))


def test_snooze_until_tomorrow():
    prefs = default_update_preferences()
    prefs["update_check_on_startup"] = True
    prefs["update_snooze_until"] = snooze_until(1, date(2026, 6, 9))

    assert not should_check_for_updates(prefs, date(2026, 6, 9))
    assert should_check_for_updates(prefs, date(2026, 6, 10))


def test_snooze_until_10_days():
    prefs = default_update_preferences()
    prefs["update_check_on_startup"] = True
    prefs["update_snooze_until"] = snooze_until(10, date(2026, 6, 9))

    assert not should_check_for_updates(prefs, date(2026, 6, 18))
    assert should_check_for_updates(prefs, date(2026, 6, 19))


def test_snooze_until_30_days():
    prefs = default_update_preferences()
    prefs["update_check_on_startup"] = True
    prefs["update_snooze_until"] = snooze_until(30, date(2026, 6, 9))

    assert not should_check_for_updates(prefs, date(2026, 7, 8))
    assert should_check_for_updates(prefs, date(2026, 7, 9))

