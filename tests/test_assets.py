from __future__ import annotations

from datetime import date


def _asset_payload(name: str = "Unit 1", status: str = "active") -> dict:
    return {
        "name": name,
        "category": "gas_turbine",
        "status": status,
        "location": "Plant A",
        "capacity_mw": 175.5,
        "installed_at": date(2018, 5, 1).isoformat(),
    }


def test_create_asset(client):
    response = client.post("/assets", json=_asset_payload())
    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "Unit 1"
    assert payload["capacity_mw"] == 175.5
    assert payload["status"] == "active"
    assert payload["work_orders"] == []


def test_create_asset_duplicate_name_returns_conflict(client):
    first = client.post("/assets", json=_asset_payload(name="Unit X"))
    assert first.status_code == 201
    duplicate = client.post("/assets", json=_asset_payload(name="Unit X"))
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "Asset with this name already exists"


def test_list_assets_can_filter_by_status(client):
    client.post("/assets", json=_asset_payload(name="Unit Alpha", status="active"))
    client.post("/assets", json=_asset_payload(name="Unit Beta", status="maintenance"))

    response = client.get("/assets", params={"status": "maintenance"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Unit Beta"
    assert data[0]["status"] == "maintenance"
