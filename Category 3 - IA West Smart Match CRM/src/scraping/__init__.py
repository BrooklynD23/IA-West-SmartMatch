"""Web scraping pipeline for university event discovery."""

from src.scraping.scraper import (
    UNIVERSITY_TARGETS,
    scrape_all_universities,
    scrape_university,
)

__all__ = [
    "UNIVERSITY_TARGETS",
    "scrape_all_universities",
    "scrape_university",
]
