#!/usr/bin/env python3
"""Collect low-volume Bilibili comment keyword candidates.

This script is intentionally conservative. It counts configured phrase hits in
selected comment pages and writes aggregate counts only, not bulk comment text.
Promote useful candidates into data/xin-sanguo-memes.json by hand.
"""

from __future__ import annotations

import argparse
import collections
import re
import datetime as dt
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_USER_AGENT = "CheeseKirby-xin-sanguo-index/0.1 (+https://github.com/CheeseKirby/memes)"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def fetch_json(url: str, user_agent: str) -> Any:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "Referer": "https://www.bilibili.com/",
            "User-Agent": user_agent,
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return json.loads(response.read().decode(charset, errors="replace"))


def aid_for_bvid(bvid: str, user_agent: str) -> int:
    payload = fetch_json(f"https://api.bilibili.com/x/web-interface/view?bvid={urllib.parse.quote(bvid)}", user_agent)
    if payload.get("code") != 0:
        raise RuntimeError(f"view API failed for {bvid}: {payload.get('message')}")
    return int(payload["data"]["aid"])


def clean_comment(value: str) -> str:
    value = re.sub(r"\[[^\]]+\]", "", value)
    value = re.sub(r"回复\s*@[^:：]+[:：]", "", value)
    value = re.sub(r"https?://\S+", "", value)
    value = re.sub(r"\s+", "", value)
    return value.strip()


def phrase_variants(value: str) -> set[str]:
    compact = re.sub(r"[，,。！？!?；;、：:\s]+", "", value)
    variants = {value, compact}
    return {variant for variant in variants if variant}


def short_phrase_candidates(message: str) -> list[str]:
    message = clean_comment(message)
    pieces = [message]
    pieces.extend(re.split(r"[，,。！？!?；;、：:\n]", message))
    result: list[str] = []
    for piece in pieces:
        piece = piece.strip()
        if not re.search(r"[\u4e00-\u9fff]", piece):
            continue
        if len(piece) < 3 or len(piece) > 18:
            continue
        if re.fullmatch(r"哈+", piece):
            continue
        if piece in {"哈哈哈", "笑死", "来了", "第一", "支持", "太好笑了"}:
            continue
        result.append(piece)
    return list(dict.fromkeys(result))


def flatten_reply_messages(reply: dict[str, Any]) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    content = (reply.get("content") or {}).get("message") or ""
    if content:
        messages.append({"message": content, "like": int(reply.get("like") or 0)})
    for child in reply.get("replies") or []:
        child_content = (child.get("content") or {}).get("message") or ""
        if child_content:
            messages.append({"message": child_content, "like": int(child.get("like") or 0)})
    return messages


def fetch_comments(aid: int, page: int, page_size: int, user_agent: str) -> list[dict[str, Any]]:
    url = f"https://api.bilibili.com/x/v2/reply?type=1&oid={aid}&sort=2&pn={page}&ps={page_size}"
    payload = fetch_json(url, user_agent)
    if payload.get("code") != 0:
        raise RuntimeError(f"reply API failed for aid {aid}: {payload.get('message')}")
    replies = (payload.get("data") or {}).get("replies") or []
    comments: list[dict[str, Any]] = []
    for reply in replies:
        comments.extend(flatten_reply_messages(reply))
    return comments


def collect(targets_path: Path, lexicon_path: Path, output_path: Path, max_pages: int, page_size: int, user_agent: str) -> int:
    targets = load_json(targets_path, {"targets": []}).get("targets", [])
    phrases = load_json(lexicon_path, {"phrases": []}).get("phrases", [])
    previous = load_json(output_path, {"videos": []})
    previous_by_bvid = {video["bvid"]: video for video in previous.get("videos", []) if video.get("bvid")}
    phrase_counts: dict[str, collections.Counter[str]] = {}
    candidate_counts: dict[str, collections.Counter[str]] = {}
    candidate_likes: dict[str, collections.Counter[str]] = {}
    target_order: list[str] = []
    page_size = max(1, min(page_size, 20))

    for target in targets:
        bvid = target.get("bvid")
        if not bvid:
            continue
        target_order.append(bvid)
        counter: collections.Counter[str] = collections.Counter()
        candidate_counter: collections.Counter[str] = collections.Counter()
        like_counter: collections.Counter[str] = collections.Counter()
        try:
            aid = aid_for_bvid(bvid, user_agent)
            for page in range(1, max_pages + 1):
                for comment in fetch_comments(aid, page, page_size, user_agent):
                    message = comment["message"]
                    cleaned = clean_comment(message)
                    for phrase in phrases:
                        if phrase and any(variant in cleaned for variant in phrase_variants(phrase)):
                            counter[phrase] += 1
                    for candidate in short_phrase_candidates(message):
                        candidate_counter[candidate] += 1
                        like_counter[candidate] += int(comment.get("like") or 0)
                time.sleep(1)
        except Exception as exc:
            print(f"Skipped {bvid}: {exc}", file=sys.stderr)
            continue
        phrase_counts[bvid] = counter
        candidate_counts[bvid] = candidate_counter
        candidate_likes[bvid] = like_counter

    videos: list[dict[str, Any]] = []
    emitted: set[str] = set()
    for bvid in target_order:
        if bvid in emitted:
            continue
        emitted.add(bvid)
        if bvid in phrase_counts:
            videos.append(
                {
                    "bvid": bvid,
                    "url": f"https://www.bilibili.com/video/{bvid}",
                    "lexicon_hits": [{"phrase": phrase, "count": count} for phrase, count in phrase_counts[bvid].most_common()],
                    "short_phrase_candidates": [
                        {
                            "phrase": phrase,
                            "count": count,
                            "like_sum": candidate_likes[bvid][phrase],
                        }
                        for phrase, count in candidate_counts[bvid].most_common(20)
                    ],
                }
            )
        elif bvid in previous_by_bvid:
            videos.append(previous_by_bvid[bvid])

    payload = {
        "schema": "https://github.com/CheeseKirby/memes/schema/bilibili-comment-candidates/v1",
        "updated_at": utc_now(),
        "notes": [
            "Only aggregate phrase counts are stored.",
            "Do not promote candidates into the main index without human review."
        ],
        "videos": videos,
    }
    write_json(output_path, payload)
    return len(payload["videos"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect Bilibili comment keyword candidates.")
    parser.add_argument("--targets", default=str(ROOT / "data" / "bilibili-comment-targets.json"))
    parser.add_argument("--lexicon", default=str(ROOT / "data" / "comment-lexicon.json"))
    parser.add_argument("--output", default=str(ROOT / "data" / "comment-candidates.json"))
    parser.add_argument("--max-pages", type=int, default=1)
    parser.add_argument("--page-size", type=int, default=20)
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    args = parser.parse_args()

    count = collect(
        targets_path=Path(args.targets),
        lexicon_path=Path(args.lexicon),
        output_path=Path(args.output),
        max_pages=args.max_pages,
        page_size=args.page_size,
        user_agent=args.user_agent,
    )
    print(f"Wrote comment candidates for {count} videos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
