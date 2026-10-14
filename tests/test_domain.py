import json
from datetime import datetime, timedelta, timezone
from backend.store import now
from scripts.hook_agent import sanitize


def attrs(sid="s1", pid="p1", rid="req_1"):
    return {
        "session.id": sid,
        "prompt.id": pid,
        "request_id": rid,
        "model": "claude-sonnet-4-6",
        "input_tokens": 100,
        "output_tokens": 20,
        "cache_read_tokens": 400,
        "cache_creation_tokens": 50,
        "cost_usd": 0.02,
    }


def hook(store, pid="p1", sid="s1", **kwargs):
    return store.hook(
        "real",
        {
            "session_id": sid,
            "prompt_id": pid,
            "event": "UserPromptSubmit",
            "event_id": sid + pid + "start",
            **kwargs,
        },
    )


def bind(store, wi="42", phase="apply", sid="s1", **kwargs):
    store.bind(
        "real",
        sid,
        {
            "work_item": wi,
            "change_id": "test-change",
            "phase": phase,
            "developer": "tester",
            "scope": "future",
            **kwargs,
        },
    )


def test_request_deduplication(ledger):
    assert ledger.request("real", attrs(), now()) == "accepted"
    assert ledger.request("real", attrs(), now()) == "duplicates"
    assert len(ledger.dashboard("real")["requests"]) == 1


def test_same_id_isolated_by_session_and_source(ledger):
    for source, sid in [("real", "s1"), ("real", "s2"), ("demo", "s1")]:
        assert ledger.request(source, attrs(sid=sid), now()) == "accepted"
    assert len(ledger.dashboard("real")["requests"]) == 2
    assert len(ledger.dashboard("demo")["requests"]) == 1


def test_snapshot_survives_late_request_after_binding_change(ledger):
    bind(ledger, phase="planning")
    hook(ledger)
    bind(ledger, wi="99", phase="apply")
    ledger.request("real", attrs(), now())
    r = ledger.dashboard("real")["requests"][0]
    assert (r["work_item"], r["phase"], r["developer"]) == ("42", "planning", "tester")


def test_orphan_resolves_on_hook_arrival(ledger):
    bind(ledger)
    ledger.request("real", attrs(), now())
    assert ledger.dashboard("real")["requests"][0]["work_item"] == ""
    hook(ledger)
    assert ledger.dashboard("real")["requests"][0]["work_item"] == "42"


def test_late_hook_uses_binding_timeline_not_current_session(ledger):
    bind(ledger, wi="42", phase="planning")
    timestamp = now()
    bind(ledger, wi="99", phase="apply")
    hook(ledger, timestamp=timestamp)
    ledger.request("real", attrs(), now())
    r = ledger.dashboard("real")["requests"][0]
    assert (r["work_item"], r["phase"]) == ("42", "planning")


def test_hook_before_any_binding_stays_unassigned(ledger):
    timestamp = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
    bind(ledger)
    hook(ledger, timestamp=timestamp)
    ledger.request("real", attrs(), now())
    assert ledger.dashboard("real")["requests"][0]["work_item"] == ""


def test_explicit_retrospective_update_and_audit(ledger):
    hook(ledger)
    ledger.request("real", attrs(), now())
    bind(ledger, scope="prompt", prompt_id="p1", phase="verify")
    r = ledger.dashboard("real")["requests"][0]
    assert r["phase"] == "verify" and r["attribution"] == "manual"
    assert len(ledger.dashboard("real")["audit"]) == 1


def test_retroactive_session_binding_resolves_queued_old_hook(ledger):
    timestamp = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    bind(ledger, scope="session")
    hook(ledger, timestamp=timestamp)
    ledger.request("real", attrs(), now())
    assert ledger.dashboard("real")["requests"][0]["work_item"] == "42"


def test_future_does_not_relabel_started_prompt(ledger):
    hook(ledger)
    bind(ledger)
    ledger.request("real", attrs(), now())
    assert ledger.dashboard("real")["requests"][0]["work_item"] == ""


def test_no_session_is_invalid(ledger):
    assert ledger.request("real", {}, now()) == "invalid"
    assert not ledger.dashboard("real")["requests"]


def test_partial_counters_flagged(ledger):
    a = attrs()
    del a["cache_creation_tokens"]
    ledger.request("real", a, now())
    assert "partial" in ledger.dashboard("real")["requests"][0]["identity_quality"]


def test_fallback_identity_flagged_and_stable_when_timestamp_present(ledger):
    a = attrs()
    del a["request_id"]
    timestamp = now()
    ledger.request("real", a, timestamp)
    ledger.request("real", a, timestamp)
    rs = ledger.dashboard("real")["requests"]
    assert len(rs) == 1 and rs[0]["identity_quality"] == "fallback"


def test_command_phase_is_coarse_planning(ledger):
    hook(ledger, phase_hint="planning", command="/opsx:propose")
    ledger.request("real", attrs(), now())
    assert ledger.dashboard("real")["requests"][0]["phase"] == "planning"


def test_hook_duplicate_and_stop(ledger):
    assert hook(ledger) == "accepted"
    assert hook(ledger) == "duplicates"
    ledger.hook(
        "real",
        {"session_id": "s1", "prompt_id": "p1", "event_id": "stop1", "event": "Stop"},
    )
    assert ledger.dashboard("real")["prompts"][0]["status"] == "completed"


def test_metadata_only_hook_and_project_scope(tmp_path):
    secret = "PRIVATE_PROMPT_ABC123"
    meta = sanitize(
        {
            "hook_event_name": "UserPromptSubmit",
            "session_id": "s1",
            "prompt_id": "p1",
            "cwd": str(tmp_path),
            "prompt": "/opsx:propose " + secret,
            "last_assistant_message": secret,
        },
        str(tmp_path),
    )
    assert secret not in json.dumps(meta)
    assert meta["phase_hint"] == "planning"
    assert (
        sanitize(
            {"hook_event_name": "SessionStart", "session_id": "s", "cwd": "/unrelated"},
            str(tmp_path),
        )
        is None
    )


def test_cost_unknown_not_zero(ledger):
    a = attrs()
    del a["cost_usd"]
    ledger.request("real", a, now())
    assert ledger.dashboard("real")["requests"][0]["cost_usd"] is None


def test_negative_cost_is_unknown(ledger):
    a = attrs()
    a["cost_usd"] = -1
    ledger.request("real", a, now())
    assert ledger.dashboard("real")["requests"][0]["cost_usd"] is None


def test_stop_can_arrive_before_submit(ledger):
    started = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    ledger.hook(
        "real",
        {
            "session_id": "s1",
            "prompt_id": "p1",
            "event": "Stop",
            "event_id": "stop-first",
            "timestamp": now(),
        },
    )
    hook(ledger, timestamp=started)
    assert ledger.dashboard("real")["prompts"][0]["status"] == "completed"


def test_stop_failure_and_session_end(ledger):
    hook(ledger)
    ledger.hook(
        "real",
        {
            "session_id": "s1",
            "prompt_id": "p1",
            "event": "StopFailure",
            "event_id": "fail1",
        },
    )
    assert ledger.dashboard("real")["prompts"][0]["status"] == "error"
    hook(ledger, pid="p2")
    ledger.hook("real", {"session_id": "s1", "event": "SessionEnd", "event_id": "end1"})
    assert ledger.dashboard("real")["sessions"][0]["status"] == "ended"
    assert any(
        p["status"] == "interrupted" for p in ledger.dashboard("real")["prompts"]
    )
