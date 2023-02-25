import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api import app
from src.services import SearchService


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def search_service():
    return SearchService(location="Kemps")


def test_get_cached_products_parsed(client, search_service):
    patch.object(search_service, "parse_items", return_value=["item1", "item2"])
    search_service.parsed_items = ["item1", "item2"]

    response = client.get("/v1/products")

    assert response.status_code == 200
    assert response.json() == ["item1", "item2"]

#
# def test_get_cached_deals(client, search_service, mocker):
#     search_service.collection_items = {"collection1": ["item1", "item2"]}
#
#     response = client.get("/v1/products/cached")
#
#     assert response.status_code == 200
#     assert response.json() == {"collection1": ["item1", "item2"]}
#
#
# def test_root(client, search_service, mocker):
#     mocker.patch.object(search_service, "run", return_value=["item1", "item2"])
#
#     response = client.get("/v1/products/fetch")
#
#     assert response.status_code == 200
#     assert response.json() == ["item1", "item2"]
#
#
# def test_get_value_from_redis(client, search_service, mocker):
#     search_service.load_from_redis = MagicMock(return_value={"key": "value"})
#
#     response = client.get("/redis/test")
#
#     assert response.status_code == 200
#     assert response.json() == {"key": "test", "value": {"key": "value"}}
#
#
# def test_get_all_values_from_redis(client, search_service, mocker):
#     search_service.redis.keys = MagicMock(return_value=["key1", "key2"])
#     search_service.load_from_redis = MagicMock(
#         side_effect=[{"key": "value1"}, {"key": "value2"}]
#     )
#
#     response = client.get("/redis")
#
#     assert response.status_code == 200
#     assert response.json() == [
#         {"key": "key1", "value": {"key": "value1"}},
#         {"key": "key2", "value": {"key": "value2"}},
#     ]
