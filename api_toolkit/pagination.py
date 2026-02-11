"""Pagination utilities for API responses."""

from dataclasses import dataclass
from typing import Generic, TypeVar, List, Optional, Any
from math import ceil

T = TypeVar("T")


@dataclass
class PaginationParams:
    page: int = 1
    per_page: int = 20
    max_per_page: int = 100

    def __post_init__(self):
        self.page = max(1, self.page)
        self.per_page = max(1, min(self.per_page, self.max_per_page))

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page

    @property
    def limit(self) -> int:
        return self.per_page


@dataclass
class PaginatedResponse(Generic[T]):
    items: List[T]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool

    @classmethod
    def create(cls, items: List[T], total: int, params: PaginationParams) -> "PaginatedResponse[T]":
        pages = ceil(total / params.per_page) if total > 0 else 1
        return cls(
            items=items,
            total=total,
            page=params.page,
            per_page=params.per_page,
            pages=pages,
            has_next=params.page < pages,
            has_prev=params.page > 1,
        )

    def to_dict(self, item_serializer=None) -> dict:
        items = [item_serializer(i) if item_serializer else i for i in self.items]
        return {
            "items": items,
            "pagination": {
                "total": self.total,
                "page": self.page,
                "per_page": self.per_page,
                "pages": self.pages,
                "has_next": self.has_next,
                "has_prev": self.has_prev,
            },
        }


def paginate_list(items: List[Any], params: PaginationParams) -> PaginatedResponse:
    """Paginate an in-memory list."""
    total = len(items)
    start = params.offset
    end = start + params.limit
    page_items = items[start:end]
    return PaginatedResponse.create(page_items, total, params)