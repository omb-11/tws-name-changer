import re
from pathlib import Path

WEBSITE_DIR = Path("website")
DIST_DIR = WEBSITE_DIR / "dist"
CHECKSUM_FILE = Path("dist/TWSNameChanger.exe.sha256")


def test_website_dist_built():
    assert DIST_DIR.exists(), "Website dist directory should exist after build"
    index_html = DIST_DIR / "index.html"
    assert index_html.exists(), "index.html must exist in website dist"
    content = index_html.read_text(encoding="utf-8")
    assert "TWS Name Changer" in content


def test_website_source_download_urls():
    app_tsx = WEBSITE_DIR / "src" / "App.tsx"
    assert app_tsx.exists()
    content = app_tsx.read_text(encoding="utf-8")

    # Verify download URL structure
    assert "https://github.com/omb-11/tws-name-changer/releases/latest/download/TWSNameChanger.exe" in content
    assert "https://github.com/omb-11/tws-name-changer" in content


def test_website_checksum_matches_release_binary():
    assert CHECKSUM_FILE.exists()
    expected_hash = CHECKSUM_FILE.read_text(encoding="utf-8").split()[0].upper()

    app_tsx = WEBSITE_DIR / "src" / "App.tsx"
    content = app_tsx.read_text(encoding="utf-8")

    assert expected_hash in content, f"Expected checksum {expected_hash} must be present in website App.tsx"


def test_website_version_consistency():
    app_tsx = WEBSITE_DIR / "src" / "App.tsx"
    content = app_tsx.read_text(encoding="utf-8")
    assert "v1.0.0" in content
    assert "Version 1.0.0" in content
