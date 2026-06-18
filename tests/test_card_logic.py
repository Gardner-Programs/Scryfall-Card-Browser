"""Tests for the pure pagination math and image-URI selection.

No Kivy or HTTP needed. The pagination cases are the off-by-one-prone bits:
mapping the app's 50-per-page views onto Scryfall's 175-per-API-page feed.
"""

import pytest

from card_logic import api_pages_for, card_image_source, max_page_count, page_offset

# --------------------------------------------------------------------------
# api_pages_for: which Scryfall API pages cover a given app page.
# (page_size 50, api_page_size 175 unless noted)
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "app_page, expected",
    [
        (1, [1]),        # cards 0-49   -> API page 1
        (3, [1]),        # cards 100-149 -> still API page 1
        (4, [1, 2]),     # cards 150-199 -> straddles the 175 boundary
        (5, [2]),        # cards 200-249 -> API page 2
    ],
)
def test_api_pages_for_size_50(app_page, expected):
    assert list(api_pages_for(app_page, 50)) == expected


def test_api_pages_for_when_page_size_equals_api_page():
    assert list(api_pages_for(1, 175)) == [1]
    assert list(api_pages_for(2, 175)) == [2]


# --------------------------------------------------------------------------
# page_offset: index into the concatenated API results where the app page starts.
# --------------------------------------------------------------------------

def test_page_offset_within_first_api_page():
    # App page 4 (cards 150-199) lives in API pages 1-2 (concatenated from idx 0).
    assert page_offset(4, 50, first_api_page=1) == 150


def test_page_offset_accounts_for_skipped_api_pages():
    # App page 5 (cards 200-249); fetch starts at API page 2 (global idx 175),
    # so the local offset is 200 - 175 = 25.
    assert page_offset(5, 50, first_api_page=2) == 25


# --------------------------------------------------------------------------
# max_page_count: app pages needed for N results.
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "num_results, expected",
    [(100, 2), (101, 3), (50, 1), (0, 0)],
)
def test_max_page_count(num_results, expected):
    assert max_page_count(num_results, 50) == expected


# --------------------------------------------------------------------------
# card_image_source: single-faced vs double-faced cards.
# --------------------------------------------------------------------------

def test_image_source_single_faced():
    card = {"image_uris": {"normal": "front.png", "small": "front_s.png"}}
    assert card_image_source(card, "normal") == "front.png"


def test_image_source_double_faced_falls_back_to_first_face():
    card = {"card_faces": [
        {"image_uris": {"normal": "face0.png"}},
        {"image_uris": {"normal": "face1.png"}},
    ]}
    assert card_image_source(card, "normal") == "face0.png"
