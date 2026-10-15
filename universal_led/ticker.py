"""Sport-agnostic ticker content and deterministic rotation.

Content providers (MLB news, other sports, weather, custom messages) can
publish TickerItems without coupling the scheduler to a particular league.
Fetching and display integration are deliberately separate concerns.
"""
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class TickerItem:
    source: str
    text: str
    category: str = 'news'
    priority: int = 0
    url: str | None = None

    def __post_init__(self):
        if not self.source.strip() or not self.text.strip():
            raise ValueError('Ticker source and text are required')
        if not isinstance(self.priority, int) or isinstance(self.priority, bool):
            raise ValueError('Ticker priority must be an integer')


def normalize_items(items: Iterable[TickerItem], *, max_items: int = 30) -> list[TickerItem]:
    """Deduplicate content while retaining priority and provider order."""
    if max_items < 1:
        raise ValueError('max_items must be positive')
    seen = set()
    unique = []
    for item in items:
        key = (item.source.casefold(), ' '.join(item.text.split()).casefold())
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return sorted(unique, key=lambda item: -item.priority)[:max_items]


def active_item(items: Iterable[TickerItem], elapsed: float, seconds: float = 15) -> TickerItem | None:
    """Return an item for a stable time slot, or None when the feed is empty."""
    if seconds <= 0:
        raise ValueError('seconds must be positive')
    ordered = normalize_items(items)
    if not ordered:
        return None
    return ordered[int(max(0, elapsed) // seconds) % len(ordered)]
