"""Tests for the web scraping pipeline (src/scraping/scraper.py)."""

import hashlib
import json
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, AsyncMock

import pytest


# ---------------------------------------------------------------------------
# SSRF validation tests
# ---------------------------------------------------------------------------

class TestValidatePublicDemoUrl:
    """Tests for validate_public_demo_url()."""

    def test_rejects_localhost(self) -> None:
        from src.scraping.scraper import validate_public_demo_url

        with pytest.raises(ValueError, match="Localhost"):
            validate_public_demo_url("http://localhost/evil")

    def test_rejects_private_ips(self) -> None:
        from src.scraping.scraper import validate_public_demo_url

        with patch("socket.getaddrinfo") as mock_gai:
            # Simulate DNS resolving to a private IP
            mock_gai.return_value = [
                (2, 1, 6, "", ("192.168.1.1", 80)),
            ]
            with pytest.raises(ValueError, match="public internet host"):
                validate_public_demo_url("http://evil.edu/path")

    def test_rejects_non_http(self) -> None:
        from src.scraping.scraper import validate_public_demo_url

        with pytest.raises(ValueError, match="http:// or https://"):
            validate_public_demo_url("ftp://career.ucla.edu/events/")

    def test_accepts_edu_domains(self) -> None:
        from src.scraping.scraper import validate_public_demo_url

        with patch("socket.getaddrinfo") as mock_gai:
            # Simulate DNS resolving to a public IP
            mock_gai.return_value = [
                (2, 1, 6, "", ("52.10.20.30", 80)),
            ]
            # Should not raise for .edu domains
            validate_public_demo_url("https://example.edu/events")


# ---------------------------------------------------------------------------
# Cache tests
# ---------------------------------------------------------------------------

class TestCacheKey:
    """Tests for _cache_key()."""

    def test_deterministic(self) -> None:
        from src.scraping.scraper import _cache_key

        url = "https://career.ucla.edu/events/"
        expected = hashlib.sha256(url.encode()).hexdigest()
        assert _cache_key(url) == expected
        # Calling again produces the same result
        assert _cache_key(url) == expected


class TestSaveAndLoadCache:
    """Tests for save_to_cache() and load_from_cache()."""

    def test_save_and_load(self, tmp_path: "pytest.TempPathFactory") -> None:
        from src.scraping.scraper import save_to_cache, load_from_cache

        url = "https://career.ucla.edu/events/"
        html = "<html><body>Hello</body></html>"
        cache_dir = str(tmp_path)

        path = save_to_cache(url, html, "bs4", cache_dir=cache_dir)
        assert path.endswith(".json")

        loaded = load_from_cache(url, cache_dir=cache_dir)
        assert loaded is not None
        assert loaded["html"] == html
        assert loaded["url"] == url
        assert loaded["method"] == "bs4"

    def test_cache_ttl_expiration(self, tmp_path: "pytest.TempPathFactory") -> None:
        from src.scraping.scraper import (
            save_to_cache,
            load_from_cache,
            _cache_path,
            CACHE_TTL_HOURS,
        )

        url = "https://career.ucla.edu/events/"
        cache_dir = str(tmp_path)
        save_to_cache(url, "<html/>", "bs4", cache_dir=cache_dir)

        # Manually backdate the scraped_at to force expiration
        path = _cache_path(url, cache_dir)
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        expired_time = datetime.utcnow() - timedelta(hours=CACHE_TTL_HOURS + 1)
        data["scraped_at"] = expired_time.isoformat()
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh)

        assert load_from_cache(url, cache_dir=cache_dir) is None


# ---------------------------------------------------------------------------
# robots.txt tests
# ---------------------------------------------------------------------------

class TestCheckRobotsTxt:
    """Tests for check_robots_txt()."""

    def test_allowed(self) -> None:
        from src.scraping.scraper import check_robots_txt

        with patch(
            "src.scraping.scraper.RobotFileParser"
        ) as MockRobotFileParser:
            rp_instance = MagicMock()
            rp_instance.can_fetch.return_value = True
            MockRobotFileParser.return_value = rp_instance

            assert check_robots_txt("https://career.ucla.edu/events/") is True

    def test_disallowed(self) -> None:
        from src.scraping.scraper import check_robots_txt

        with patch(
            "src.scraping.scraper.RobotFileParser"
        ) as MockRobotFileParser:
            rp_instance = MagicMock()
            rp_instance.can_fetch.return_value = False
            MockRobotFileParser.return_value = rp_instance

            assert check_robots_txt("https://career.ucla.edu/events/") is False


# ---------------------------------------------------------------------------
# Rate limiter test
# ---------------------------------------------------------------------------

class TestRateLimit:
    """Tests for _rate_limit()."""

    def test_enforces_delay(self) -> None:
        import src.scraping.scraper as scraper_mod

        with patch.object(scraper_mod, "_last_request_time", time.time()):
            with patch("time.sleep") as mock_sleep:
                scraper_mod._rate_limit()
                # sleep should have been called since we just set _last_request_time
                mock_sleep.assert_called_once()
                args = mock_sleep.call_args[0]
                assert args[0] > 0


# ---------------------------------------------------------------------------
# Scraping backend tests
# ---------------------------------------------------------------------------

class TestScrapeBS4:
    """Tests for _scrape_bs4()."""

    def test_success(self) -> None:
        import src.scraping.scraper as scraper_mod

        with patch("src.scraping.scraper.requests.get") as mock_get, \
             patch("time.sleep"):
            mock_response = MagicMock()
            mock_response.text = "<html>UCLA Events</html>"
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            # Reset rate limiter
            scraper_mod._last_request_time = 0.0
            html = scraper_mod._scrape_bs4("https://career.ucla.edu/events/")
            assert html == "<html>UCLA Events</html>"
            mock_get.assert_called_once()


class TestScrapePlaywright:
    """Tests for _scrape_playwright()."""

    def test_success(self) -> None:
        import src.scraping.scraper as scraper_mod

        with patch("time.sleep"):
            # Reset rate limiter
            scraper_mod._last_request_time = 0.0

            mock_page = AsyncMock()
            mock_page.content.return_value = "<html>SDSU Events</html>"
            mock_page.goto = AsyncMock()

            mock_browser = AsyncMock()
            mock_browser.new_page.return_value = mock_page
            mock_browser.close = AsyncMock()

            mock_chromium = AsyncMock()
            mock_chromium.launch.return_value = mock_browser

            mock_pw = AsyncMock()
            mock_pw.chromium = mock_chromium

            mock_pw_ctx = AsyncMock()
            mock_pw_ctx.__aenter__ = AsyncMock(return_value=mock_pw)
            mock_pw_ctx.__aexit__ = AsyncMock(return_value=False)

            with patch(
                "playwright.async_api.async_playwright",
                return_value=mock_pw_ctx,
            ):
                html = scraper_mod._scrape_playwright(
                    "https://www.sdsu.edu/events-calendar"
                )
                assert html == "<html>SDSU Events</html>"


# ---------------------------------------------------------------------------
# Public API tests
# ---------------------------------------------------------------------------

class TestScrapeUniversity:
    """Tests for scrape_university()."""

    def test_returns_cache_on_hit(self, tmp_path: "pytest.TempPathFactory") -> None:
        from src.scraping.scraper import (
            save_to_cache,
            scrape_university,
        )

        url = "https://career.ucla.edu/events/"
        cache_dir = str(tmp_path)
        save_to_cache(url, "<html>cached</html>", "bs4", cache_dir=cache_dir)

        with patch("socket.getaddrinfo") as mock_gai:
            mock_gai.return_value = [(2, 1, 6, "", ("52.10.20.30", 80))]
            result = scrape_university(url, method="bs4", cache_dir=cache_dir)

        assert result["source"] == "cache"
        assert result["html"] == "<html>cached</html>"

    def test_raises_on_robots_deny(self, tmp_path: "pytest.TempPathFactory") -> None:
        from src.scraping.scraper import scrape_university

        url = "https://career.ucla.edu/events/"
        cache_dir = str(tmp_path)

        with patch("socket.getaddrinfo") as mock_gai, \
             patch("src.scraping.scraper.check_robots_txt", return_value=False):
            mock_gai.return_value = [(2, 1, 6, "", ("52.10.20.30", 80))]
            with pytest.raises(PermissionError, match="robots.txt disallows"):
                scrape_university(url, method="bs4", cache_dir=cache_dir)


class TestScrapeAllUniversities:
    """Tests for scrape_all_universities()."""

    def test_handles_failures(self, tmp_path: "pytest.TempPathFactory") -> None:
        from src.scraping.scraper import scrape_all_universities

        cache_dir = str(tmp_path)

        with patch(
            "src.scraping.scraper.scrape_university",
            side_effect=RuntimeError("Network error"),
        ):
            results = scrape_all_universities(cache_dir=cache_dir)

        # All 5 universities should have error entries
        assert len(results) == 5
        for name, result in results.items():
            assert result["source"] == "failed"
            assert "error" in result
