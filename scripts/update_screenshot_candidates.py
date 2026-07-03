#!/usr/bin/env python3
"""Build screenshot source candidates without downloading full videos.

The output stores BVIDs, source links, target repository paths, and Bilibili
videoshot storyboard URLs. scripts/generate_screenshots.py can crop selected
storyboard cells into assets/screenshots/.
"""

from __future__ import annotations

import argparse
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


def absolute_url(value: str | None) -> str | None:
    if not value:
        return None
    if value.startswith("//"):
        return f"https:{value}"
    return value


def fetch_json(url: str, user_agent: str, referer: str) -> Any:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "Referer": referer,
            "User-Agent": user_agent,
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return json.loads(response.read().decode(charset, errors="replace"))


def videoshot_for(episode: dict[str, Any], user_agent: str) -> dict[str, Any]:
    aid = episode.get("aid")
    cid = episode.get("cid")
    bvid = episode.get("bvid")
    if not aid or not cid or not bvid:
        return {"status": "unavailable", "reason": "missing aid/cid/bvid"}

    query = urllib.parse.urlencode({"aid": aid, "cid": cid})
    payload = fetch_json(
        f"https://api.bilibili.com/x/player/videoshot?{query}",
        user_agent=user_agent,
        referer=f"https://www.bilibili.com/video/{bvid}",
    )
    if payload.get("code") != 0:
        return {"status": "unavailable", "reason": payload.get("message") or "api_error"}

    data = payload.get("data") or {}
    return {
        "status": "source_preview",
        "pvdata_url": absolute_url(data.get("pvdata")),
        "image_urls": [absolute_url(url) for url in data.get("image", []) if absolute_url(url)],
        "grid": {
            "columns": data.get("img_x_len"),
            "rows": data.get("img_y_len"),
            "cell_width": data.get("img_x_size"),
            "cell_height": data.get("img_y_size"),
        },
        "note": "B 站 videoshot 预览帧网格，用于定位截图画面。",
    }


def find_item(items: list[dict[str, Any]], item_id: str) -> dict[str, Any] | None:
    for item in items:
        if item.get("id") == item_id:
            return item
    return None


def build_candidates(
    targets_path: Path,
    curated_path: Path,
    series_path: Path,
    output_path: Path,
    user_agent: str,
    sleep_seconds: float,
) -> int:
    targets = load_json(targets_path, {"targets": []}).get("targets", [])
    curated_items = load_json(curated_path, {"items": []}).get("items", [])
    episodes = load_json(series_path, {"episodes": []}).get("episodes", [])
    episodes_by_bvid = {episode["bvid"]: episode for episode in episodes if episode.get("bvid")}

    result_items: list[dict[str, Any]] = []
    for target in targets:
        item_id = target.get("item_id")
        item = find_item(curated_items, item_id)
        if not item:
            print(f"Skipped {item_id}: item not found", file=sys.stderr)
            continue

        bvid = target.get("bvid") or item.get("primary_bvid")
        episode = episodes_by_bvid.get(bvid or "")
        storyboard: dict[str, Any]
        if episode:
            try:
                storyboard = videoshot_for(episode, user_agent)
                time.sleep(sleep_seconds)
            except Exception as exc:
                storyboard = {"status": "unavailable", "reason": str(exc)}
        else:
            storyboard = {"status": "unavailable", "reason": "episode not found"}

        result_items.append(
            {
                "item_id": item_id,
                "title": item.get("title"),
                "bvid": bvid,
                "source_url": f"https://www.bilibili.com/video/{bvid}" if bvid else item.get("source_url"),
                "episode": episode.get("episode") if episode else None,
                "episode_title": episode.get("title") if episode else None,
                "priority": target.get("priority", 3),
                "frame_hint": target.get("frame_hint", ""),
                "repository_image_path": f"assets/screenshots/{item_id}.jpg",
                "storyboard": storyboard,
            }
        )

    write_json(
        output_path,
        {
            "schema": "https://github.com/CheeseKirby/memes/schema/screenshot-candidates/v1",
            "updated_at": utc_now(),
            "notes": [
                "这是一批明确梗的截图来源清单。",
                "B 站预览帧网格用于定位画面，也可由 scripts/generate_screenshots.py 自动裁图。",
                "scripts/update_index.py 会优先使用 assets/screenshots/ 中已存在的截图。"
            ],
            "item_count": len(result_items),
            "items": result_items,
        },
    )
    return len(result_items)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build screenshot source candidate metadata.")
    parser.add_argument("--targets", default=str(ROOT / "data" / "screenshot-targets.json"))
    parser.add_argument("--curated", default=str(ROOT / "data" / "xin-sanguo-memes.json"))
    parser.add_argument("--series", default=str(ROOT / "data" / "bilibili-series.json"))
    parser.add_argument("--output", default=str(ROOT / "data" / "screenshot-candidates.json"))
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    parser.add_argument("--sleep", type=float, default=0.2)
    args = parser.parse_args()

    count = build_candidates(
        targets_path=Path(args.targets),
        curated_path=Path(args.curated),
        series_path=Path(args.series),
        output_path=Path(args.output),
        user_agent=args.user_agent,
        sleep_seconds=args.sleep,
    )
    print(f"Wrote {count} screenshot source candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
