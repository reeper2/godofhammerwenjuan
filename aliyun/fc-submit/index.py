# -*- coding: utf-8 -*-
"""阿里云函数计算 HTTP 触发：接收问卷 JSON，写入 OSS。"""
import json
import os
import uuid
from datetime import datetime, timezone

import oss2

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json; charset=utf-8",
}


def _response(status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "headers": CORS_HEADERS,
        "body": json.dumps(body, ensure_ascii=False),
    }


def _parse_event(event):
    if isinstance(event, (bytes, str)):
        event = json.loads(event)
    method = (
        event.get("requestContext", {}).get("http", {}).get("method")
        or event.get("httpMethod")
        or "POST"
    )
    body_raw = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        import base64

        body_raw = base64.b64decode(body_raw).decode("utf-8")
    return method.upper(), body_raw


def _get_bucket():
    endpoint = os.environ["OSS_ENDPOINT"]
    if not endpoint.startswith("http"):
        endpoint = "https://" + endpoint
    auth = oss2.Auth(os.environ["OSS_ACCESS_KEY_ID"], os.environ["OSS_ACCESS_KEY_SECRET"])
    return oss2.Bucket(auth, endpoint, os.environ["OSS_BUCKET"])


def handler(event, context):
    try:
        method, body_raw = _parse_event(event)
        if method == "OPTIONS":
            return {"statusCode": 204, "headers": CORS_HEADERS, "body": ""}

        if method != "POST":
            return _response(405, {"ok": False, "error": "method not allowed"})

        token = os.environ.get("SURVEY_TOKEN", "").strip()
        if token:
            try:
                evt = event if isinstance(event, dict) else json.loads(event)
                headers = {k.lower(): v for k, v in (evt.get("headers") or {}).items()}
            except Exception:
                headers = {}
            if headers.get("x-survey-token") != token:
                return _response(403, {"ok": False, "error": "forbidden"})

        data = json.loads(body_raw)
        payload = data.get("payload") if isinstance(data.get("payload"), dict) else data
        if not isinstance(payload, dict):
            return _response(400, {"ok": False, "error": "invalid payload"})

        prefix = os.environ.get("OSS_PREFIX", "survey-responses/").lstrip("/")
        if prefix and not prefix.endswith("/"):
            prefix += "/"
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        key = f"{prefix}{ts}_{uuid.uuid4().hex}.json"

        record = {
            "submittedAt": payload.get("submittedAt") or datetime.now(timezone.utc).isoformat(),
            "company_name": payload.get("company_name", ""),
            "industry": payload.get("industry", ""),
            "ent_type": payload.get("entType", ""),
            "payload": payload,
        }

        bucket = _get_bucket()
        bucket.put_object(
            key,
            json.dumps(record, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
        )

        return _response(200, {"ok": True, "key": key})
    except Exception as exc:
        return _response(500, {"ok": False, "error": str(exc)})
