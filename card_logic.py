"""Pure card-browsing logic: Scryfall pagination math and image-URI selection.

No Kivy and no HTTP — just the arithmetic that maps the app's pages onto
Scryfall's fixed 175-cards-per-page API, and the rule for pulling an image URI
out of a card dict (handling double-faced cards). start.py imports these.
"""

from __future__ import annotations

import math

# Scryfall returns a fixed number of cards per API page.
SCRYFALL_PAGE_SIZE = 175


def api_pages_for(app_page: int, page_size: int, api_page_size: int = SCRYFALL_PAGE_SIZE) -> range:
    """Return the Scryfall API page numbers needed to fill one app page.

    The app shows *page_size* cards per view; Scryfall serves *api_page_size*
    per request, so a single app page can straddle two API pages.
    """
    first = ((app_page - 1) * page_size) // api_page_size + 1
    last = ((app_page * page_size) - 1) // api_page_size + 1
    return range(first, last + 1)


def page_offset(
    app_page: int,
    page_size: int,
    first_api_page: int,
    api_page_size: int = SCRYFALL_PAGE_SIZE,
) -> int:
    """Index into the concatenated API-page results where this app page starts."""
    return ((app_page - 1) * page_size) - ((first_api_page - 1) * api_page_size)


def max_page_count(num_results: int, page_size: int) -> int:
    """Number of app pages needed to show *num_results* cards."""
    return math.ceil(num_results / page_size)


def card_image_source(card: dict, img_name: str) -> str:
    """Return the image URI for *img_name*.

    Single-faced cards carry a top-level ``image_uris``; double-faced cards have
    none and instead expose images under the first entry of ``card_faces``.
    """
    try:
        return card["image_uris"][img_name]
    except KeyError:
        return card["card_faces"][0]["image_uris"][img_name]
