from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOTYPE_DIR = REPO_ROOT / "prototypes" / "v2_concept_comparison"

REQUIRED_FILES = [
    "index.html",
    "feedback.html",
    "README.md",
    "assets/i18n.js",
    "assets/locked_loading_soon.png",
    "assets/locked_loading_soon_closed.png",
    "concept_a_program_shell/index.html",
    "concept_a_program_shell/app.js",
    "concept_a_program_shell/styles.css",
    "concept_a_program_shell/module-realism.css",
    "concept_b_workshop_companion/index.html",
    "concept_b_workshop_companion/app.js",
    "concept_b_workshop_companion/styles.css",
    "concept_b_workshop_companion/module-realism.css",
]

MAIN_PAGES = [
    "index.html",
    "feedback.html",
    "concept_a_program_shell/index.html",
    "concept_b_workshop_companion/index.html",
]

TEXT_SUFFIXES = {".html", ".css", ".js"}
HTML_ATTR_RE = re.compile(r"""(?:href|src)\s*=\s*(['"])(.*?)\1""", re.IGNORECASE)
URL_RE = re.compile(r"""(?<![A-Za-z0-9_])url\(\s*(['"]?)(.*?)\1\s*\)""", re.IGNORECASE)
EXTERNAL_MARKERS = [
    "http://",
    "https://",
    "cdn.",
    "fonts.googleapis",
    "unpkg",
    "jsdelivr",
]


# These are intentionally static smoke checks, not full browser or UI tests.
# They protect against broken links, missing assets, missing language markers,
# and accidental external dependencies without judging whether the design is good.


def prototype_path(relative_path):
    return PROTOTYPE_DIR / relative_path


def text_files():
    return sorted(
        path for path in PROTOTYPE_DIR.rglob("*") if path.is_file() and path.suffix in TEXT_SUFFIXES
    )


def html_files():
    return sorted(PROTOTYPE_DIR.rglob("*.html"))


def read_text(path):
    return path.read_text(encoding="utf-8")


def is_ignored_reference(value):
    stripped = value.strip()
    lower = stripped.lower()
    return (
        not stripped
        or stripped.startswith("#")
        or lower.startswith("mailto:")
        or lower.startswith("data:")
        or lower.startswith("javascript:")
        or lower.startswith("http://")
        or lower.startswith("https://")
    )


def resolve_local_reference(source_file, value):
    parsed = urlsplit(value.strip())
    path_part = unquote(parsed.path)
    if not path_part:
        return None
    return (source_file.parent / path_part).resolve()


def assert_reference_exists(source_file, value):
    target = resolve_local_reference(source_file, value)
    if target is None:
        return
    assert target.exists(), f"{source_file.relative_to(REPO_ROOT)} references missing file {value!r}"


def test_required_v2_concept_files_exist():
    missing = [path for path in REQUIRED_FILES if not prototype_path(path).exists()]
    assert not missing, f"Missing required v2 concept prototype files: {missing}"


def test_html_href_and_src_references_are_local_and_existing():
    broken = []
    for html_file in html_files():
        for _, value in HTML_ATTR_RE.findall(read_text(html_file)):
            if is_ignored_reference(value):
                continue
            target = resolve_local_reference(html_file, value)
            if target is not None and not target.exists():
                broken.append((html_file.relative_to(REPO_ROOT), value))

    assert not broken, f"Broken local href/src references: {broken}"


def test_css_url_references_are_local_and_existing():
    broken = []
    for source_file in text_files():
        for _, value in URL_RE.findall(read_text(source_file)):
            stripped = value.strip()
            lower = stripped.lower()
            if (
                is_ignored_reference(stripped)
                or lower.startswith("var(")
                or lower.startswith("attr(")
            ):
                continue
            target = resolve_local_reference(source_file, stripped)
            if target is not None and not target.exists():
                broken.append((source_file.relative_to(REPO_ROOT), stripped))

    assert not broken, f"Broken local CSS url(...) references: {broken}"


def test_prototype_has_no_external_network_dependencies():
    allowed_svg_namespace = "http://www.w3.org/2000/svg"
    offenders = []

    for source_file in text_files():
        content = read_text(source_file).replace(allowed_svg_namespace, "")
        lower = content.lower()
        for marker in EXTERNAL_MARKERS:
            if marker in lower:
                offenders.append((source_file.relative_to(REPO_ROOT), marker))

    assert not offenders, f"External network dependency markers found: {offenders}"


def test_main_pages_have_language_switch_markers():
    for relative_path in MAIN_PAGES:
        content = read_text(prototype_path(relative_path))
        assert "data-language-switch" in content
        assert 'data-lang="de"' in content
        assert 'data-lang="en"' in content


def test_main_pages_reference_shared_i18n_helper():
    assert prototype_path("assets/i18n.js").exists()
    assert 'src="assets/i18n.js"' in read_text(prototype_path("index.html"))
    assert 'src="assets/i18n.js"' in read_text(prototype_path("feedback.html"))
    assert 'src="../assets/i18n.js"' in read_text(
        prototype_path("concept_a_program_shell/index.html")
    )
    assert 'src="../assets/i18n.js"' in read_text(
        prototype_path("concept_b_workshop_companion/index.html")
    )


def test_feedback_form_contains_local_feedback_behavior_markers():
    content = read_text(prototype_path("feedback.html"))
    for marker in [
        'id="generateMarkdown"',
        'id="copyMarkdown"',
        'id="downloadMarkdown"',
        "Blob",
        "URL.createObjectURL",
        "navigator.clipboard",
        'id="markdownOutput"',
    ]:
        assert marker in content


def test_prototype_readme_documents_static_local_scope():
    content = read_text(prototype_path("README.md")).lower()
    for marker in [
        "static html/css/js",
        "no backend",
        "no upload",
        "no network connection",
        "no machine output",
        "german and english",
        "download feedback",
    ]:
        assert marker in content
