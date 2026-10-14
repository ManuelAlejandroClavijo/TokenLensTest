"""OTLP JSON / protobuf adapter. Extract only a strict metadata allowlist."""

from datetime import datetime, timezone
from .store import now

ALLOWED = {
    "session.id",
    "prompt.id",
    "request_id",
    "client_request_id",
    "event.sequence",
    "event.timestamp",
    "model",
    "input_tokens",
    "output_tokens",
    "cache_read_tokens",
    "cache_creation_tokens",
    "cost_usd",
    "cost_usd_micros",
    "duration_ms",
    "query_source",
    "tool_name",
    "tool_use_id",
    "tool_input_size_bytes",
    "tool_result_size_bytes",
    "success",
    "type",
    "event.name",
    "event_name",
}


def value(v):
    if not isinstance(v, dict):
        return v
    for k in ("stringValue", "intValue", "doubleValue", "boolValue", "bytesValue"):
        if k in v:
            return v[k]
    return None


def attributes(items):
    return {
        x["key"]: value(x.get("value", {}))
        for x in items
        if isinstance(x, dict) and x.get("key") in ALLOWED
    }


def timestamp(record, attrs):
    try:
        if attrs.get("event.timestamp"):
            dt = datetime.fromisoformat(
                str(attrs["event.timestamp"]).replace("Z", "+00:00")
            )
            return (
                dt.replace(tzinfo=dt.tzinfo or timezone.utc)
                .astimezone(timezone.utc)
                .isoformat()
            )
        n = record.get("timeUnixNano") or record.get("observedTimeUnixNano")
        if n:
            return datetime.fromtimestamp(int(n) / 1e9, timezone.utc).isoformat()
    except (ValueError, TypeError, OverflowError, OSError):
        pass
    return now()


def ingest_logs(store, data, source="real"):
    counts = {k: 0 for k in ("accepted", "duplicates", "ignored", "invalid")}
    for resource in data.get("resourceLogs", []):
        base = attributes(resource.get("resource", {}).get("attributes", []))
        for scope in resource.get(
            "scopeLogs", resource.get("instrumentationLibraryLogs", [])
        ):
            for rec in scope.get("logRecords", []):
                attrs = {**base, **attributes(rec.get("attributes", []))}
                event = (
                    attrs.get("event.name")
                    or attrs.get("event_name")
                    or value(rec.get("body", {}))
                    or rec.get("eventName")
                    or ""
                )
                if not isinstance(event, str):
                    counts["ignored"] += 1
                    continue
                event = event.removeprefix("claude_code.")
                time = timestamp(rec, attrs)
                if event in ("api_request", "api_error"):
                    result = store.request(source, attrs, time, event)
                elif event == "tool_result":
                    result = store.tool(source, attrs, time)
                else:
                    # user_prompt is intentionally not persisted: hooks delimit turns without text.
                    result = "ignored"
                counts[result] += 1
    store.receipt(source, "logs", counts)
    return counts


def ingest_metrics(store, data, source="real"):
    counts = {k: 0 for k in ("accepted", "duplicates", "ignored", "invalid")}
    for resource in data.get("resourceMetrics", []):
        base = attributes(resource.get("resource", {}).get("attributes", []))
        for scope in resource.get("scopeMetrics", []):
            for metric in scope.get("metrics", []):
                if metric.get("name") != "claude_code.token.usage":
                    counts["ignored"] += 1
                    continue
                summed = metric.get("sum", {})
                temporality = summed.get("aggregationTemporality", 0)
                if isinstance(temporality, str):
                    temporality = {
                        "AGGREGATION_TEMPORALITY_CUMULATIVE": 2,
                        "AGGREGATION_TEMPORALITY_DELTA": 1,
                    }.get(temporality, 0)
                for point in summed.get("dataPoints", []):
                    attrs = {**base, **attributes(point.get("attributes", []))}
                    counts[store.metric(source, attrs, point, temporality)] += 1
    store.receipt(source, "metrics", counts)
    return counts
