"""Deterministic, isolated synthetic fixture. Never presented as a real capture."""

import random
from datetime import datetime, timezone, timedelta


def seed(store):
    store.clear_demo()
    rng = random.Random(27)
    base = datetime.now(timezone.utc) - timedelta(hours=8)
    examples = [
        (
            "demo-auth",
            "1842",
            "refresh-token-resilience",
            "payments-api",
            "planning",
            6,
        ),
        ("demo-checkout", "1837", "checkout-timeouts", "checkout-service", "apply", 12),
        ("demo-otel", "1851", "otel-collector-health", "platform-infra", "verify", 5),
    ]
    n = 0
    for sid, wi, change, repo, phase, count in examples:
        store.hook(
            "demo",
            {
                "session_id": sid,
                "event_id": sid + "start",
                "event": "SessionStart",
                "repo": repo,
                "timestamp": base.isoformat(),
            },
        )
        store.bind(
            "demo",
            sid,
            {
                "work_item": wi,
                "change_id": change,
                "phase": phase,
                "developer": "local-user",
                "scope": "future",
            },
        )
        for p in range(count):
            pid = f"{sid}-prompt-{p}"
            t = base + timedelta(minutes=n * 5)
            store.hook(
                "demo",
                {
                    "session_id": sid,
                    "prompt_id": pid,
                    "event_id": pid + "start",
                    "event": "UserPromptSubmit",
                    "timestamp": t.isoformat(),
                    "command": "/opsx:apply" if phase == "apply" else "/opsx:propose",
                },
            )
            for j in range(rng.randint(2, 5)):
                n += 1
                attrs = {
                    "session.id": sid,
                    "prompt.id": pid,
                    "request_id": f"req_demo_{n}",
                    "event.sequence": n,
                    "model": "claude-sonnet-4-6" if (n % 9) else "claude-opus-4-6",
                    "input_tokens": rng.randint(800, 5000),
                    "output_tokens": rng.randint(200, 2200),
                    "cache_read_tokens": rng.randint(7000, 32000),
                    "cache_creation_tokens": rng.randint(1200, 8000),
                    "duration_ms": rng.randint(2400, 19000),
                    "query_source": "subagent" if n % 5 == 0 else "main",
                }
                attrs["cost_usd"] = round(
                    attrs["input_tokens"] * 3e-6
                    + attrs["output_tokens"] * 15e-6
                    + attrs["cache_read_tokens"] * 0.3e-6
                    + attrs["cache_creation_tokens"] * 3.75e-6,
                    6,
                )
                store.request(
                    "demo", attrs, (t + timedelta(seconds=j * 20)).isoformat()
                )
                store.tool(
                    "demo",
                    {
                        "session.id": sid,
                        "prompt.id": pid,
                        "event.sequence": n,
                        "tool_name": "mcp__azure__get_work_item"
                        if n % 4 == 0
                        else "Read",
                        "tool_input_size_bytes": 300,
                        "tool_result_size_bytes": rng.randint(1500, 82000),
                        "duration_ms": rng.randint(80, 700),
                        "success": n % 17 != 0,
                    },
                    t.isoformat(),
                )
            store.hook(
                "demo",
                {
                    "session_id": sid,
                    "prompt_id": pid,
                    "event_id": pid + "stop",
                    "event": "Stop",
                    "timestamp": (t + timedelta(minutes=2)).isoformat(),
                },
            )
    store.receipt(
        "demo", "logs", {"accepted": n, "duplicates": 3, "ignored": 12, "invalid": 0}
    )
