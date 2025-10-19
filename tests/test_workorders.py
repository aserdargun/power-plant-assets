from __future__ import annotations

from datetime import date


def _asset_payload(name: str = "Unit 99") -> dict:
    return {
        "name": name,
        "category": "solar",
        "status": "active",
        "location": "Plant B",
        "capacity_mw": 85.0,
        "installed_at": date(2020, 7, 15).isoformat(),
    }


def _work_order_payload(asset_id: int, title: str = "Inspect bearings") -> dict:
    return {
        "asset_id": asset_id,
        "title": title,
        "description": "Perform standard vibration analysis.",
        "status": "open",
        "priority": "high",
        "scheduled_start": date(2024, 5, 1).isoformat(),
        "scheduled_end": date(2024, 5, 2).isoformat(),
    }


def _create_asset(client, name: str = "Unit 99") -> dict:
    response = client.post("/assets", json=_asset_payload(name))
    assert response.status_code == 201
    return response.json()


def test_create_work_order_for_existing_asset(client):
    asset = _create_asset(client, "Unit Z")
    response = client.post("/workorders", json=_work_order_payload(asset_id=asset["id"]))
    assert response.status_code == 201
    payload = response.json()
    assert payload["asset_id"] == asset["id"]
    assert payload["title"] == "Inspect bearings"
    assert payload["priority"] == "high"
    assert payload["status"] == "open"


def test_create_work_order_for_missing_asset_returns_404(client):
    response = client.post("/workorders", json=_work_order_payload(asset_id=999))
    assert response.status_code == 404
    assert response.json()["detail"] == "Related asset not found"


def test_update_work_order_status_and_completion(client):
    asset = _create_asset(client, "Unit Q")
    create_response = client.post(
        "/workorders", json=_work_order_payload(asset_id=asset["id"], title="Oil change")
    )
    work_order = create_response.json()

    patch_payload = {"status": "completed"}
    patch_response = client.patch(f"/workorders/{work_order['id']}", json=patch_payload)
    assert patch_response.status_code == 200
    assert patch_response.json()["status"] == "completed"


def test_list_work_orders_can_filter_by_asset(client):
    asset_a = _create_asset(client, "Unit F")
    asset_b = _create_asset(client, "Unit G")

    client.post("/workorders", json=_work_order_payload(asset_id=asset_a["id"], title="Task A"))
    client.post("/workorders", json=_work_order_payload(asset_id=asset_b["id"], title="Task B"))

    response = client.get("/workorders", params={"asset_id": asset_a["id"]})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Task A"
    assert data[0]["asset_id"] == asset_a["id"]
