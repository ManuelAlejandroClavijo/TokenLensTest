import gzip
import json
from google.protobuf.json_format import ParseDict
from opentelemetry.proto.collector.logs.v1.logs_service_pb2 import (
    ExportLogsServiceRequest,
)
from backend import app as mod


def envelope(sid="s1", event="claude_code.api_request", extra=None):
    attrs = {
        "session.id": sid,
        "prompt.id": "p1",
        "request_id": "req_test",
        "model": "claude-sonnet-4-6",
        "input_tokens": 100,
        "output_tokens": 20,
        "cache_read_tokens": 400,
        "cache_creation_tokens": 50,
        "cost_usd": 0.02,
    }
    attrs.update(extra or {})
    items = []
    for k, v in attrs.items():
        kind = (
            "boolValue"
            if isinstance(v, bool)
            else "doubleValue"
            if isinstance(v, float)
            else "intValue"
            if isinstance(v, int)
            else "stringValue"
        )
        items.append({"key": k, "value": {kind: str(v) if kind == "intValue" else v}})
    return {
        "resourceLogs": [
            {
                "scopeLogs": [
                    {
                        "logRecords": [
                            {
                                "timeUnixNano": "1791979200000000000",
                                "body": {"stringValue": event},
                                "attributes": items,
                            }
                        ]
                    }
                ]
            }
        ]
    }


def test_otlp_json_duplicate(client, auth):
    assert client.post("/v1/logs", json=envelope(), headers=auth).status_code == 200
    assert client.post("/v1/logs", json=envelope(), headers=auth).status_code == 200
    d = client.get("/api/dashboard").json()
    assert len(d["requests"]) == 1
    assert d["receipts"][0]["duplicates"] == 1


def test_otlp_protobuf(client, auth):
    msg = ParseDict(envelope(), ExportLogsServiceRequest())
    result = client.post(
        "/v1/logs",
        content=msg.SerializeToString(),
        headers={**auth, "Content-Type": "application/x-protobuf"},
    )
    assert result.status_code == 200
    assert result.headers["content-type"] == "application/x-protobuf"
    assert client.get("/api/dashboard").json()["requests"][0]["input_tokens"] == 100


def test_gzip(client, auth):
    result = client.post(
        "/v1/logs",
        content=gzip.compress(json.dumps(envelope()).encode()),
        headers={
            **auth,
            "Content-Type": "application/json",
            "Content-Encoding": "gzip",
        },
    )
    assert result.status_code == 200


def test_authentication(client):
    assert client.post("/v1/logs", json=envelope()).status_code == 401
    assert client.post("/hooks", json={}).status_code == 401


def test_cross_origin_and_host_rejected(client):
    assert (
        client.post("/api/demo", headers={"Origin": "https://evil.test"}).status_code
        == 403
    )
    assert (
        client.get("/api/dashboard", headers={"Host": "evil.test"}).status_code == 403
    )


def test_privacy_no_sensitive_fields_stored(client, auth):
    secret = "NEVER_STORE_PRIVATE_CODE_ABC"
    client.post(
        "/v1/logs",
        json=envelope(
            extra={
                "prompt": secret,
                "user.email": secret,
                "api_request_body": secret,
                "tool_parameters": secret,
            }
        ),
        headers=auth,
    )
    assert secret not in json.dumps(client.get("/api/dashboard").json())
    assert secret not in mod.store.path.read_bytes().decode("latin1")


def test_metrics_snapshots_not_added_to_ledger(client, auth):
    client.post("/v1/logs", json=envelope(), headers=auth)
    data = {
        "resourceMetrics": [
            {
                "resource": {
                    "attributes": [
                        {"key": "session.id", "value": {"stringValue": "s1"}}
                    ]
                },
                "scopeMetrics": [
                    {
                        "metrics": [
                            {
                                "name": "claude_code.token.usage",
                                "sum": {
                                    "aggregationTemporality": 2,
                                    "dataPoints": [
                                        {
                                            "asInt": "100",
                                            "startTimeUnixNano": "10",
                                            "timeUnixNano": "20",
                                            "attributes": [
                                                {
                                                    "key": "type",
                                                    "value": {"stringValue": "input"},
                                                }
                                            ],
                                        }
                                    ],
                                },
                            }
                        ]
                    }
                ],
            }
        ]
    }
    client.post("/v1/metrics", json=data, headers=auth)
    client.post("/v1/metrics", json=data, headers=auth)
    d = client.get("/api/dashboard").json()
    assert len(d["metrics"]) == 1
    assert len(d["requests"]) == 1 and d["requests"][0]["input_tokens"] == 100


def test_demo_isolated_and_delete_only_demo(client, auth):
    client.post("/v1/logs", json=envelope(), headers=auth)
    assert client.post("/api/demo").status_code == 200
    assert len(client.get("/api/dashboard?source=demo").json()["requests"]) > 0
    assert len(client.get("/api/dashboard").json()["requests"]) == 1
    client.delete("/api/demo")
    assert len(client.get("/api/dashboard").json()["requests"]) == 1


def test_binding_export_and_reconciliation(client, auth):
    client.post("/v1/logs", json=envelope(), headers=auth)
    body = {
        "work_item": "42",
        "change_id": "=danger()",
        "phase": "planning",
        "scope": "session",
    }
    assert client.put("/api/sessions/s1/binding", json=body).status_code == 200
    exported = client.get("/api/export.csv")
    assert exported.status_code == 200
    assert "'=danger()" in exported.text
    result = client.post(
        "/api/reconcile",
        json={
            "session_id": "s1",
            "input_tokens": 100,
            "output_tokens": 20,
            "cache_read_tokens": 400,
            "cache_creation_tokens": 50,
        },
    ).json()
    assert all(v == 0 for v in result["delta"].values())


def test_invalid_protocol_and_payload(client, auth):
    assert (
        client.post(
            "/v1/logs", content="xxx", headers={**auth, "Content-Type": "text/plain"}
        ).status_code
        == 415
    )
    assert (
        client.post(
            "/v1/logs",
            content="xxx",
            headers={**auth, "Content-Type": "application/json"},
        ).status_code
        == 400
    )
    assert (
        client.post("/v1/logs", json={"plain": "event"}, headers=auth).status_code
        == 400
    )
    assert (
        client.post("/v1/logs", json={"resourceLogs": 4}, headers=auth).status_code
        == 400
    )


def test_missing_session_partial_success(client, auth):
    result = client.post("/v1/logs", json=envelope(sid=""), headers=auth)
    assert result.json()["partialSuccess"]["rejectedLogRecords"] == "1"


def test_hook_payload_is_filtered_by_contract(client, auth):
    raw = {
        "session_id": "s1",
        "prompt_id": "p1",
        "event_id": "hook-1",
        "event": "UserPromptSubmit",
        "prompt": "SECRET",
    }
    assert client.post("/hooks", json=raw, headers=auth).status_code == 200
    assert "SECRET" not in client.get("/api/dashboard").text


def test_invalid_phase_rejected(client, auth):
    client.post("/v1/logs", json=envelope(), headers=auth)
    assert (
        client.put("/api/sessions/s1/binding", json={"phase": "invented"}).status_code
        == 422
    )


def test_frontend_is_served(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "<html" in r.text


def test_compressed_body_limit(client, auth):
    huge = gzip.compress(b"a" * 8_000_100)
    result = client.post(
        "/v1/logs",
        content=huge,
        headers={
            **auth,
            "Content-Type": "application/json",
            "Content-Encoding": "gzip",
        },
    )
    assert result.status_code == 413


def test_csv_search_filter(client, auth):
    client.post("/v1/logs", json=envelope(), headers=auth)
    assert (
        "req_test" in client.get("/api/export.csv?q=req_test").text
        or "req_test" in client.get("/api/export.csv?q=s1").text
    )
    assert "req_test" not in client.get("/api/export.csv?q=no-match").text


def test_tool_result_and_unknown_event(client, auth):
    client.post(
        "/v1/logs",
        json=envelope(
            event="claude_code.tool_result",
            extra={
                "tool_name": "Read",
                "tool_result_size_bytes": 75000,
                "success": True,
            },
        ),
        headers=auth,
    )
    client.post(
        "/v1/logs",
        json=envelope(event="claude_code.user_prompt", extra={"prompt": "NEVER_STORE"}),
        headers=auth,
    )
    d = client.get("/api/dashboard").json()
    assert len(d["tools"]) == 1 and d["tools"][0]["output_bytes"] == 75000
    assert not d["requests"]
    assert d["receipts"][0]["ignored"] == 1
