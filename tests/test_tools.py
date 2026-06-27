import pytest
from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0

def test_search_empty_results():
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []

def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=10)
    assert all(item["price"] <= 10 for item in results)

def test_search_returns_at_most_three():
    results = search_listings("shirt", size=None, max_price=100)
    assert len(results) <= 3

def test_search_size_filter():
    results = search_listings("jeans", size="W30", max_price=100)
    assert all("30" in item["size"] for item in results)

def test_search_no_exception_on_empty_description():
    results = search_listings("", size=None, max_price=100)
    assert isinstance(results, list)


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def test_suggest_outfit_returns_string():
    results = search_listings("jeans", size=None, max_price=50)
    wardrobe = get_example_wardrobe()
    result = suggest_outfit(results[0], wardrobe)
    assert isinstance(result, str)
    assert len(result) > 0

def test_suggest_outfit_empty_wardrobe():
    results = search_listings("jeans", size=None, max_price=50)
    empty = get_empty_wardrobe()
    result = suggest_outfit(results[0], empty)
    assert result == ""


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def test_create_fit_card_returns_string():
    results = search_listings("jeans", size=None, max_price=50)
    wardrobe = get_example_wardrobe()
    outfit = suggest_outfit(results[0], wardrobe)
    fit_card = create_fit_card(outfit, results[0])
    assert isinstance(fit_card, str)
    assert len(fit_card) > 0

def test_create_fit_card_empty_outfit():
    results = search_listings("jeans", size=None, max_price=50)
    result = create_fit_card("", results[0])
    assert "Error:" in result

def test_create_fit_card_whitespace_outfit():
    results = search_listings("jeans", size=None, max_price=50)
    result = create_fit_card("   ", results[0])
    assert "Error:" in result