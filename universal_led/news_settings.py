"""Validated, persistent configuration for reusable RSS/Atom news sources."""
import json
import os
import tempfile
from pathlib import Path

from .news_feeds import NewsSource

FILENAME = 'news_sources.json'


def validate_news_settings(data):
    if not isinstance(data, dict) or set(data) != {'sources'} or not isinstance(data['sources'], list):
        raise ValueError('Expected an object with a sources list')
    if len(data['sources']) > 20:
        raise ValueError('At most 20 news sources are supported')
    sources = []
    names = set()
    for item in data['sources']:
        if not isinstance(item, dict) or set(item) - {'name', 'url', 'category', 'enabled', 'refresh_seconds'}:
            raise ValueError('Invalid news source fields')
        try:
            source = NewsSource(**item)
        except (TypeError, AttributeError) as exc:
            raise ValueError('Invalid news source') from exc
        name = source.name.strip()
        if name.casefold() in names:
            raise ValueError('News source names must be unique')
        names.add(name.casefold())
        sources.append({'name': name, 'url': source.url, 'category': source.category.strip(),
                        'enabled': source.enabled, 'refresh_seconds': source.refresh_seconds})
    return {'sources': sources}


def load_news_settings(config_dir):
    path = Path(config_dir) / FILENAME
    if not path.exists():
        return {'sources': []}
    return validate_news_settings(json.loads(path.read_text(encoding='utf-8')))


def save_news_settings(config_dir, data):
    normalized = validate_news_settings(data)
    directory = Path(config_dir)
    directory.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.news-', suffix='.tmp', dir=directory)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(normalized, stream, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, directory / FILENAME)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return normalized
