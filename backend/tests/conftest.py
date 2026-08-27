"""Pytest configuration and shared fixtures for backend tests."""

from pathlib import Path

import pytest
from django.core.files.storage import FileSystemStorage, default_storage, storages
from django.test import Client


@pytest.fixture(autouse=True)
def isolated_media_root(
    tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch, settings
) -> Path:
    """Isolate MEDIA_ROOT and default_storage during tests so test cleanups never touch development media."""
    media_dir = tmp_path_factory.mktemp("test_media")
    settings.MEDIA_ROOT = media_dir

    test_storage = FileSystemStorage(location=str(media_dir))
    monkeypatch.setitem(storages._storages, "default", test_storage)
    monkeypatch.setattr(default_storage, "_wrapped", test_storage)

    return media_dir


@pytest.fixture
def client() -> Client:
    """Provide a standard Django test client."""
    return Client()
