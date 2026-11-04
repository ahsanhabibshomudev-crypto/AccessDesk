from sqlmodel import select

from app.models import AuditLog


def make_tool(client, name="GitHub", **extra):
    response = client.post("/api/tools", json={"name": name, **extra})
    assert response.status_code == 201, response.text
    return response.json()


# ---------- Create ----------


def test_create_tool(client):
    response = client.post(
        "/api/tools",
        json={"name": "  GitHub  ", "description": "Source code", "category": "Dev"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["id"] >= 1
    assert body["name"] == "GitHub"  # trimmed
    assert body["description"] == "Source code"
    assert body["category"] == "Dev"
    assert body["is_active"] is True
    assert "created_at" in body


def test_create_rejects_blank_or_missing_name(client):
    assert client.post("/api/tools", json={"name": "   "}).status_code == 422
    assert client.post("/api/tools", json={}).status_code == 422


def test_create_rejects_too_long_fields(client):
    assert client.post("/api/tools", json={"name": "x" * 101}).status_code == 422
    assert (
        client.post("/api/tools", json={"name": "ok", "description": "x" * 501}).status_code
        == 422
    )


def test_create_duplicate_name_is_409_ignoring_case(client):
    make_tool(client, "GitHub")
    response = client.post("/api/tools", json={"name": "github"})
    assert response.status_code == 409
    assert response.json() == {"detail": "A tool with this name already exists"}


# ---------- Read list ----------


def test_list_is_empty_at_first(client):
    response = client.get("/api/tools")
    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0, "skip": 0, "limit": 20}


def test_list_is_newest_first_and_paginated(client):
    for name in ["A", "B", "C", "D", "E"]:
        make_tool(client, name)

    first = client.get("/api/tools", params={"limit": 2}).json()
    assert [t["name"] for t in first["items"]] == ["E", "D"]
    assert first["total"] == 5

    second = client.get("/api/tools", params={"limit": 2, "skip": 2}).json()
    assert [t["name"] for t in second["items"]] == ["C", "B"]


def test_list_validates_paging_params(client):
    assert client.get("/api/tools", params={"limit": 0}).status_code == 422
    assert client.get("/api/tools", params={"limit": 101}).status_code == 422
    assert client.get("/api/tools", params={"skip": -1}).status_code == 422


# ---------- Read single ----------


def test_get_one_tool(client):
    created = make_tool(client, "Jira")
    response = client.get(f"/api/tools/{created['id']}")
    assert response.status_code == 200
    assert response.json() == created


def test_get_missing_tool_is_404(client):
    response = client.get("/api/tools/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Tool not found"}


def test_get_with_non_numeric_id_is_422(client):
    assert client.get("/api/tools/abc").status_code == 422


# ---------- Update ----------


def test_patch_changes_only_the_sent_fields(client):
    created = make_tool(client, "AWS", description="Cloud", category="Infra")
    response = client.patch(f"/api/tools/{created['id']}", json={"description": "Servers"})
    assert response.status_code == 200
    body = response.json()
    assert body["description"] == "Servers"
    assert body["name"] == "AWS"
    assert body["category"] == "Infra"


def test_patch_can_clear_optional_fields(client):
    created = make_tool(client, "AWS", description="Cloud")
    response = client.patch(f"/api/tools/{created['id']}", json={"description": ""})
    assert response.json()["description"] is None


def test_patch_to_a_taken_name_is_409_but_own_name_is_fine(client):
    make_tool(client, "GitHub")
    other = make_tool(client, "Jira")

    clash = client.patch(f"/api/tools/{other['id']}", json={"name": "github"})
    assert clash.status_code == 409

    same = client.patch(f"/api/tools/{other['id']}", json={"name": "JIRA"})
    assert same.status_code == 200
    assert same.json()["name"] == "JIRA"


def test_patch_rejects_null_name_and_blank_name(client):
    created = make_tool(client)
    url = f"/api/tools/{created['id']}"
    assert client.patch(url, json={"name": None}).status_code == 422
    assert client.patch(url, json={"name": "  "}).status_code == 422
    assert client.patch(url, json={"is_active": None}).status_code == 422


def test_patch_missing_tool_is_404(client):
    assert client.patch("/api/tools/999", json={"name": "X"}).status_code == 404


# ---------- Delete (deactivate) ----------


def test_delete_hides_the_tool_but_keeps_the_row(client):
    created = make_tool(client, "Slack")
    url = f"/api/tools/{created['id']}"

    assert client.delete(url).status_code == 204

    assert client.get("/api/tools").json()["total"] == 0
    everything = client.get("/api/tools", params={"include_inactive": True}).json()
    assert everything["total"] == 1
    assert everything["items"][0]["is_active"] is False
    assert client.get(url).json()["is_active"] is False  # still readable by id


def test_delete_twice_is_fine_and_missing_is_404(client):
    created = make_tool(client)
    url = f"/api/tools/{created['id']}"
    assert client.delete(url).status_code == 204
    assert client.delete(url).status_code == 204
    assert client.delete("/api/tools/999").status_code == 404


def test_deactivated_tool_can_be_reactivated(client):
    created = make_tool(client)
    url = f"/api/tools/{created['id']}"
    client.delete(url)
    response = client.patch(url, json={"is_active": True})
    assert response.json()["is_active"] is True
    assert client.get("/api/tools").json()["total"] == 1


# ---------- Audit log ----------


def test_every_change_writes_an_audit_entry(client, session):
    created = make_tool(client, "GitHub")
    url = f"/api/tools/{created['id']}"
    client.patch(url, json={"category": "Dev"})
    client.delete(url)
    client.get(url)  # reading does not create an entry

    entries = session.exec(select(AuditLog).order_by(AuditLog.id)).all()
    assert [e.action for e in entries] == ["tool.create", "tool.update", "tool.deactivate"]
    assert all(e.entity_type == "tool" and e.entity_id == created["id"] for e in entries)


def test_failed_requests_write_no_audit_entry(client, session):
    make_tool(client, "GitHub")
    client.post("/api/tools", json={"name": "github"})  # 409
    client.post("/api/tools", json={"name": ""})  # 422
    assert len(session.exec(select(AuditLog)).all()) == 1


# ---------- Misc ----------


def test_health_and_docs_paths(client):
    assert client.get("/api/health").json() == {"status": "ok"}
    assert client.get("/api/docs").status_code == 200
    assert client.get("/api/openapi.json").status_code == 200


def test_created_at_is_returned_as_utc(client):
    created = make_tool(client)
    assert created["created_at"].endswith(("Z", "+00:00"))
