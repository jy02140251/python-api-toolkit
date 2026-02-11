"""Tests for pagination utilities."""

import pytest
from api_toolkit.pagination import PaginationParams, PaginatedResponse, paginate_list


class TestPaginationParams:
    def test_defaults(self):
        params = PaginationParams()
        assert params.page == 1
        assert params.per_page == 20
        assert params.offset == 0
        assert params.limit == 20

    def test_custom_values(self):
        params = PaginationParams(page=3, per_page=10)
        assert params.offset == 20
        assert params.limit == 10

    def test_negative_page_clamped(self):
        params = PaginationParams(page=-1)
        assert params.page == 1

    def test_per_page_clamped_to_max(self):
        params = PaginationParams(per_page=500, max_per_page=100)
        assert params.per_page == 100


class TestPaginatedResponse:
    def test_create_response(self):
        items = [1, 2, 3]
        params = PaginationParams(page=1, per_page=10)
        response = PaginatedResponse.create(items, total=30, params=params)
        assert response.total == 30
        assert response.pages == 3
        assert response.has_next is True
        assert response.has_prev is False

    def test_last_page(self):
        params = PaginationParams(page=3, per_page=10)
        response = PaginatedResponse.create([], total=30, params=params)
        assert response.has_next is False
        assert response.has_prev is True

    def test_to_dict(self):
        items = ["a", "b"]
        params = PaginationParams(page=1, per_page=10)
        response = PaginatedResponse.create(items, total=2, params=params)
        result = response.to_dict()
        assert "items" in result
        assert "pagination" in result
        assert result["pagination"]["total"] == 2


class TestPaginateList:
    def test_paginate_first_page(self):
        items = list(range(50))
        params = PaginationParams(page=1, per_page=10)
        result = paginate_list(items, params)
        assert len(result.items) == 10
        assert result.items == list(range(10))
        assert result.total == 50

    def test_paginate_last_page(self):
        items = list(range(25))
        params = PaginationParams(page=3, per_page=10)
        result = paginate_list(items, params)
        assert len(result.items) == 5
        assert result.has_next is False

    def test_paginate_empty_list(self):
        result = paginate_list([], PaginationParams())
        assert result.total == 0
        assert result.items == []