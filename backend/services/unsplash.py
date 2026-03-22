"""Fetch images from Unsplash for PPT slides.

Uses the Unsplash JSON API (free tier: 50 requests/hour for demo apps).
Set the access key via UNSPLASH_ACCESS_KEY environment variable or pass it
directly to the functions.

If no key is configured, all functions gracefully return empty results.
"""

import asyncio
import logging
import os
import re
from typing import Optional

import httpx

logger = logging.getLogger("app.unsplash")

API_BASE = "https://api.unsplash.com"
SEARCH_URL = f"{API_BASE}/search/photos"
DEFAULT_TIMEOUT = 10.0  # seconds per request


def get_access_key() -> str:
    """Return the configured Unsplash access key, or empty string."""
    return os.environ.get("UNSPLASH_ACCESS_KEY", "")


def _keywords_from_title(title: str) -> str:
    """Extract search-friendly English-ish keywords from a slide title.

    For Chinese titles we keep them as-is — Unsplash handles CJK queries.
    We strip numbering prefixes like '1. ' and markdown formatting.
    """
    # Remove numbering prefix
    title = re.sub(r"^\d+\.\s*", "", title)
    # Remove markdown bold/italic
    title = re.sub(r"\*+", "", title)
    return title.strip()


async def search_image(
    keyword: str,
    access_key: str = "",
    width: int = 800,
    height: int = 600,
) -> Optional[bytes]:
    """Search Unsplash for *keyword* and return the first result as raw bytes.

    Returns None if no key is set, no results found, or request fails.
    """
    key = access_key or get_access_key()
    if not key:
        return None

    keyword = _keywords_from_title(keyword)
    if not keyword:
        return None

    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            # 1. Search
            resp = await client.get(
                SEARCH_URL,
                params={
                    "query": keyword,
                    "per_page": 1,
                    "orientation": "landscape",
                },
                headers={"Authorization": f"Client-ID {key}"},
            )
            resp.raise_for_status()
            data = resp.json()

            results = data.get("results", [])
            if not results:
                logger.debug("No image found for '%s'", keyword)
                return None

            # 2. Pick the small/regular URL (good enough for PPT)
            urls = results[0].get("urls", {})
            img_url = urls.get("small") or urls.get("regular") or urls.get("raw")
            if not img_url:
                return None

            # Resize via Unsplash dynamic params
            if "?" in img_url:
                img_url += f"&w={width}&h={height}&fit=crop"
            else:
                img_url += f"?w={width}&h={height}&fit=crop"

            # 3. Download
            img_resp = await client.get(img_url)
            img_resp.raise_for_status()
            logger.info("Fetched image for '%s' (%d bytes)", keyword, len(img_resp.content))
            return img_resp.content

    except Exception as e:
        logger.warning("Unsplash fetch failed for '%s': %s", keyword, e)
        return None


async def fetch_images_for_slides(
    titles: list[str],
    access_key: str = "",
    width: int = 800,
    height: int = 600,
) -> dict[int, bytes]:
    """Fetch images concurrently for a list of slide titles.

    Returns a dict mapping slide index → image bytes.
    Slides that fail or have no results are simply omitted.
    """
    key = access_key or get_access_key()
    if not key:
        return {}

    tasks = [
        search_image(title, access_key=key, width=width, height=height)
        for title in titles
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    images: dict[int, bytes] = {}
    for i, result in enumerate(results):
        if isinstance(result, bytes):
            images[i] = result
    return images
