#!/usr/bin/env python3
"""Dependency-free client for the Vidiohalo Agent API."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import uuid
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def config() -> tuple[str, str]:
    key = os.environ.get("VIDIOHALO_AGENT_KEY", "").strip()
    if not key:
        raise SystemExit("VIDIOHALO_AGENT_KEY is not configured. Create one in Vidiohalo → 个人中心 → Agent.")
    base = os.environ.get("VIDIOHALO_API_BASE_URL", "https://vidiohalo.com/api").rstrip("/")
    return base, key


def open_request(request: Request) -> object:
    try:
        with urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(detail).get("detail", detail)
        except (ValueError, AttributeError):
            pass
        raise SystemExit(f"Vidiohalo API error {error.code}: {detail}") from error
    except URLError as error:
        raise SystemExit(f"Cannot reach Vidiohalo: {error.reason}") from error


def request_json(method: str, path: str, payload: dict | None = None) -> object:
    base, key = config()
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    return open_request(Request(f"{base}{path}", data=body, method=method, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}))


def upload(path: Path) -> object:
    base, key = config()
    if not path.is_file():
        raise SystemExit(f"File not found: {path}")
    boundary = f"----vidiohalo-{uuid.uuid4().hex}"
    content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    body = b"".join([
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"rights_confirmed\"\r\n\r\ntrue\r\n".encode(),
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{path.name}\"\r\nContent-Type: {content_type}\r\n\r\n".encode(),
        path.read_bytes(),
        f"\r\n--{boundary}--\r\n".encode(),
    ])
    return open_request(Request(f"{base}/agent/v1/assets/upload", data=body, method="POST", headers={"Authorization": f"Bearer {key}", "Content-Type": f"multipart/form-data; boundary={boundary}"}))


def add_output_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--resolution", choices=["720P", "2K"], default="720P")
    parser.add_argument("--aspect-ratio", default=None)


def main() -> None:
    parser = argparse.ArgumentParser(description="Vidiohalo Agent API client")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list-assets")
    upload_parser = sub.add_parser("upload")
    upload_parser.add_argument("path", type=Path)
    upload_parser.add_argument("--rights-confirmed", action="store_true", required=True)
    status = sub.add_parser("status")
    status.add_argument("id")

    oneclick = sub.add_parser("create-oneclick")
    oneclick.add_argument("--script", required=True)
    oneclick.add_argument("--requirements", default="")
    oneclick.add_argument("--person", action="append", default=[])
    oneclick.add_argument("--voice", action="append", default=[])
    oneclick.add_argument("--product", action="append", default=[])
    oneclick.add_argument("--broll", action="append", default=[])
    speaker = oneclick.add_mutually_exclusive_group()
    speaker.add_argument("--voice-id", help="Exact stock or ready cloned voice ID from the selected site")
    speaker.add_argument("--speaker", choices=["male", "female"], help="Legacy CN stock voice selector")
    oneclick.add_argument("--speech-rate", type=int, default=0)
    add_output_options(oneclick)

    remake = sub.add_parser("create-remake")
    source = remake.add_mutually_exclusive_group(required=True)
    source.add_argument("--source-asset")
    source.add_argument("--source-url")
    remake.add_argument("--platform", choices=["direct", "wechat", "douyin", "xiaohongshu", "kuaishou", "bilibili"], default="direct")
    remake.add_argument("--requirements", required=True)
    remake.add_argument("--person", action="append", default=[])
    remake.add_argument("--product", action="append", default=[])
    remake.add_argument("--audio", action="append", default=[])
    add_output_options(remake)

    args = parser.parse_args()
    if args.command == "list-assets":
        result = request_json("GET", "/agent/v1/assets")
    elif args.command == "upload":
        result = upload(args.path)
    elif args.command == "status":
        result = request_json("GET", f"/agent/v1/creations/{args.id}")
    elif args.command == "create-oneclick":
        payload = {
            "workflow": "oneclick", "script": args.script, "requirements": args.requirements,
            "resolution": args.resolution, "aspect_ratio": args.aspect_ratio or "9:16",
            "person_asset_ids": args.person, "voice_asset_ids": args.voice,
            "product_asset_ids": args.product, "broll_asset_ids": args.broll,
            "speech_rate": args.speech_rate,
        }
        if args.voice_id:
            payload["tts_speaker"] = args.voice_id
        elif args.speaker:
            payload["tts_speaker"] = {
                "male": "zh_male_taocheng_uranus_bigtts",
                "female": "zh_female_meilinvyou_uranus_bigtts",
            }[args.speaker]
        result = request_json("POST", "/agent/v1/creations", payload)
    else:
        uses_asset = bool(args.source_asset)
        result = request_json("POST", "/agent/v1/creations", {
            "workflow": "remake", "source_kind": "asset" if uses_asset else "url",
            "source_platform": "direct" if uses_asset else args.platform,
            "source_asset_id": args.source_asset, "source_url": None if uses_asset else args.source_url,
            "requirements": args.requirements,
            "person_asset_ids": args.person, "product_asset_ids": args.product, "audio_asset_ids": args.audio,
            "resolution": args.resolution, "aspect_ratio": args.aspect_ratio or "source",
        })
    if isinstance(result, dict) and isinstance(result.get("detail_url"), str) and result["detail_url"].startswith("/"):
        base, _key = config()
        result["detail_url"] = f"{base.removesuffix('/api')}{result['detail_url']}"
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
