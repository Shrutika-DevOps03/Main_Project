import oracledb
import pytest

import api.app as api_module


@pytest.fixture
def client():
    api_module.app.config["TESTING"] = True
    return api_module.app.test_client()


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}


def test_total_orders(client, monkeypatch):
    monkeypatch.setattr(api_module, "run_query", lambda sql, params=None: [(13,)])
    response = client.get("/api/orders/total")
    assert response.status_code == 200
    assert response.get_json() == {"total_orders": 13}


def test_orders_pagination_uses_offset_and_limit(client, monkeypatch):
    calls = []

    def fake_query(sql, params=None):
        calls.append(params)
        if "COUNT" in sql:
            return [(25,)]
        return []

    monkeypatch.setattr(api_module, "run_query", fake_query)
    response = client.get("/api/orders?page=3&limit=5")
    body = response.get_json()
    assert response.status_code == 200
    assert body["page"] == 3
    assert body["total"] == 25
    assert calls[0] == {"offset": 10, "limit": 5}


@pytest.mark.parametrize("query", ["page=0", "page=abc", "limit=0", "limit=1000"])
def test_orders_rejects_bad_paging(client, query):
    response = client.get("/api/orders?" + query)
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_database_error_returns_503(client, monkeypatch):
    def broken(sql, params=None):
        raise oracledb.Error("db down")

    monkeypatch.setattr(api_module, "run_query", broken)
    response = client.get("/api/orders/total")
    assert response.status_code == 503
    assert response.get_json() == {"error": "database unavailable"}


def test_unknown_route_returns_json_404(client):
    response = client.get("/api/nothing")
    assert response.status_code == 404
    assert response.get_json() == {"error": "not found"}
