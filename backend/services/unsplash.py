"""Fetch images from Unsplash, Bing, or free sources for PPT slides.

Uses the Unsplash JSON API when an access key is provided (free tier: 50 req/hr).
Falls back to Bing image search (content-relevant, no key required), then to
picsum.photos (random images) as a last resort.
"""

import asyncio
import hashlib
import html as html_mod
import json
import logging
import os
import re
import urllib.parse
from typing import Optional

import httpx

logger = logging.getLogger("app.unsplash")

API_BASE = "https://api.unsplash.com"
SEARCH_URL = f"{API_BASE}/search/photos"
DEFAULT_TIMEOUT = 10.0  # seconds per request

_BING_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}


def get_access_key() -> str:
    """Return the configured Unsplash access key, or empty string."""
    return os.environ.get("UNSPLASH_ACCESS_KEY", "")


def _keywords_from_title(title: str) -> str:
    """Extract search-friendly keywords from a slide title.

    For Chinese titles we keep them as-is — Bing/Unsplash handles CJK queries.
    We strip numbering prefixes like '1. ' and markdown formatting.
    """
    # Remove numbering prefix
    title = re.sub(r"^\d+\.\s*", "", title)
    # Remove markdown bold/italic
    title = re.sub(r"\*+", "", title)
    return title.strip()


# ---------------------------------------------------------------------------
# Bing image search (content-relevant, no API key required)
# Scrapes Bing image search results and downloads thumbnails from Bing CDN.
# ---------------------------------------------------------------------------

async def _fetch_bing_image(
    keyword: str,
    width: int = 800,
    height: int = 600,
) -> Optional[bytes]:
    """Fetch a content-relevant image via Bing image search (no key needed).

    Searches Bing Images for the keyword, extracts thumbnail URLs from Bing's
    CDN (tse*.mm.bing.net), and downloads the first matching result.
    """
    keyword = _keywords_from_title(keyword)
    if not keyword:
        return None

    encoded_kw = urllib.parse.quote(keyword)
    search_url = (
        f"https://www.bing.com/images/search"
        f"?q={encoded_kw}&first=1&count=5"
    )

    try:
        async with httpx.AsyncClient(
            timeout=DEFAULT_TIMEOUT,
            verify=False,
            follow_redirects=True,
            headers=_BING_HEADERS,
        ) as client:
            # 1. Search Bing Images
            resp = await client.get(search_url)
            resp.raise_for_status()

            # 2. Parse m="..." attributes containing JSON with image URLs
            m_attrs = re.findall(r'm="(\{[^"]+\})"', resp.text)
            if not m_attrs:
                logger.debug("No Bing image results for '%s'", keyword)
                return None

            # 3. Extract thumbnail URLs from Bing's CDN
            for raw in m_attrs[:5]:
                decoded = html_mod.unescape(raw)
                try:
                    obj = json.loads(decoded)
                except (json.JSONDecodeError, ValueError):
                    continue

                turl = obj.get("turl", "")
                if not turl or "mm.bing.net" not in turl:
                    continue

                # 4. Download the thumbnail
                img_resp = await client.get(turl)
                if img_resp.status_code == 200 and len(img_resp.content) > 1000:
                    logger.info(
                        "Fetched Bing image for '%s' (%d bytes)",
                        keyword, len(img_resp.content),
                    )
                    return img_resp.content

            logger.debug("No downloadable Bing thumbnail for '%s'", keyword)
            return None

    except Exception as e:
        logger.warning("Bing image fetch failed for '%s': %s", keyword, e)
        return None


async def _fetch_bing_images_for_slides(
    titles: list[str],
    width: int = 800,
    height: int = 600,
) -> dict[int, bytes]:
    """Fetch content-relevant Bing images concurrently for slide titles."""
    tasks = [
        _fetch_bing_image(title, width=width, height=height)
        for title in titles
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    images: dict[int, bytes] = {}
    for i, result in enumerate(results):
        if isinstance(result, bytes):
            images[i] = result
    return images


# ---------------------------------------------------------------------------
# Picsum fallback (random images, no API key required)
# Uses picsum.photos with a deterministic seed derived from the slide title,
# so the same title always gets the same image.
# ---------------------------------------------------------------------------

async def _fetch_picsum_image(
    keyword: str,
    width: int = 800,
    height: int = 600,
) -> Optional[bytes]:
    """Fetch a random stock photo from picsum.photos (no key needed).

    Uses a hash of the keyword as seed so images are deterministic per title.
    Note: images are random and NOT related to the keyword content.
    """
    keyword = _keywords_from_title(keyword)
    if not keyword:
        return None

    seed = hashlib.md5(keyword.encode()).hexdigest()[:10]
    url = f"https://picsum.photos/seed/{seed}/{width}/{height}"

    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            if len(resp.content) > 1000:  # sanity check
                logger.info("Fetched picsum image for '%s' (%d bytes)", keyword, len(resp.content))
                return resp.content
            return None
    except Exception as e:
        logger.warning("Picsum image fetch failed for '%s': %s", keyword, e)
        return None


async def fetch_free_images_for_slides(
    titles: list[str],
    width: int = 800,
    height: int = 600,
) -> dict[int, bytes]:
    """Fetch free images for slide titles (no key needed).

    Strategy: try Bing image search first (content-relevant), then fill any
    missing slides with picsum.photos (random) as a fallback.
    """
    # 1. Try Bing for content-relevant images
    images = await _fetch_bing_images_for_slides(titles, width=width, height=height)
    logger.info("Bing provided images for %d/%d slides", len(images), len(titles))

    # 2. Fill missing slides with picsum fallback
    missing = [i for i in range(len(titles)) if i not in images]
    if missing:
        logger.info("Falling back to picsum for %d missing slides", len(missing))
        picsum_tasks = [
            _fetch_picsum_image(titles[i], width=width, height=height)
            for i in missing
        ]
        picsum_results = await asyncio.gather(*picsum_tasks, return_exceptions=True)
        for idx, result in zip(missing, picsum_results):
            if isinstance(result, bytes):
                images[idx] = result

    return images


# ---------------------------------------------------------------------------
# Unsplash (requires API key)
# ---------------------------------------------------------------------------

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

    Uses Unsplash if a key is available, otherwise falls back to free sources.
    Returns a dict mapping slide index -> image bytes.
    Slides that fail or have no results are simply omitted.
    """
    key = access_key or get_access_key()
    if not key:
        logger.info("No Unsplash key, using free image source for %d slides", len(titles))
        return await fetch_free_images_for_slides(titles, width=width, height=height)

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
