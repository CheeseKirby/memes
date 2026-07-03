#!/usr/bin/env python3
"""Build the New Three Kingdoms meme index.

The index is curated first. Automated sources are used as metadata references:
Bilibili season metadata can enrich entries with episode title, cover URL, and
source links. Existing assets under assets/screenshots/ are preferred over SVG
fallback cards when a meme has a clear screenshot.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import urllib.parse
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "https://github.com/CheeseKirby/memes/schema/xin-sanguo/v1"
RAW_BASE_URL = "https://raw.githubusercontent.com/CheeseKirby/memes/main"


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


def normalize_token(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9_\-\u4e00-\u9fff]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value


def unique_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        token = normalize_token(value)
        if token and token not in seen:
            seen.add(token)
            result.append(token)
    return result


def bvid_url(bvid: str) -> str:
    return f"https://www.bilibili.com/video/{bvid}"


def load_bilibili_episode_map(path: Path) -> dict[str, dict[str, Any]]:
    payload = load_json(path, {"episodes": []})
    episodes = payload.get("episodes", [])
    return {episode["bvid"]: episode for episode in episodes if episode.get("bvid")}


def enrich_with_bilibili(item: dict[str, Any], episodes_by_bvid: dict[str, dict[str, Any]]) -> dict[str, Any]:
    bvid = item.get("primary_bvid")
    if not bvid:
        return item

    episode = episodes_by_bvid.get(bvid)
    item.setdefault("source_url", bvid_url(bvid))
    item.setdefault("bilibili_url", bvid_url(bvid))

    if not episode:
        return item

    item["bilibili_url"] = episode.get("url") or bvid_url(bvid)
    item["episode"] = episode.get("episode")
    item["episode_title"] = episode.get("title")
    item["episode_pubdate"] = episode.get("pubdate")
    item["episode_stats"] = episode.get("stat")

    cover = episode.get("cover_url")
    if cover:
        item.setdefault("thumbnail_url", cover)
        item.setdefault("image_refs", [])
        if not any(ref.get("url") == cover for ref in item["image_refs"]):
            item["image_refs"].append(
                {
                    "kind": "bilibili_cover",
                    "status": "reference_only",
                    "url": cover,
                    "note": "Bilibili video cover URL; not rehosted by this repository."
                }
            )

    return item


def repository_asset_url(path: str) -> str:
    return f"{RAW_BASE_URL}/{path}"


def load_screenshot_candidate_map(path: Path) -> dict[str, dict[str, Any]]:
    payload = load_json(path, {"items": []})
    return {item["item_id"]: item for item in payload.get("items", []) if item.get("item_id")}


def apply_screenshot_candidate(item: dict[str, Any], screenshot_candidates: dict[str, dict[str, Any]]) -> dict[str, Any]:
    candidate = screenshot_candidates.get(item.get("id", ""))
    if not candidate:
        return item

    item.setdefault("image_refs", [])
    storyboard = candidate.get("storyboard") or {}
    image_urls = storyboard.get("image_urls") or []
    if not any(ref.get("kind") == "bilibili_videoshot_storyboard" for ref in item["image_refs"]):
        item["image_refs"].append(
            {
                "kind": "bilibili_videoshot_storyboard",
                "status": "source_preview",
                "urls": image_urls,
                "pvdata_url": storyboard.get("pvdata_url"),
                "grid": storyboard.get("grid"),
                "frame_hint": candidate.get("frame_hint"),
                "repository_image_path": candidate.get("repository_image_path"),
                "note": "用于定位和复核截图的 B 站预览帧网格。"
            }
        )

    image_path = candidate.get("repository_image_path")
    if image_path and (ROOT / image_path).exists():
        image_url = repository_asset_url(image_path)
        item["image_url"] = image_url
        item["thumbnail_url"] = image_url
        item["image_status"] = "screenshot"
        if not any(ref.get("kind") == "repository_screenshot" and ref.get("path") == image_path for ref in item["image_refs"]):
            item["image_refs"].append(
                {
                    "kind": "repository_screenshot",
                    "status": "repo_asset",
                    "path": image_path,
                    "url": image_url,
                    "note": "仓库中的新三国梗截图。"
                }
            )
    elif item.get("image_status") in {"generated_card", "video_frame_needed", "needs_curated_image"}:
        item["image_status"] = "screenshot_target"

    return item


def normalize_item(
    item: dict[str, Any],
    source_id: str,
    now: str,
    episodes_by_bvid: dict[str, dict[str, Any]],
    screenshot_candidates: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    item = dict(item)
    item["schema"] = SCHEMA
    item["source"] = source_id
    item["language"] = item.get("language") or "zh"
    item["safe"] = bool(item.get("safe", True))
    item["tags"] = unique_strings(list(item.get("tags", [])))
    item["tone"] = unique_strings(list(item.get("tone", [])))
    item["aliases"] = list(dict.fromkeys(item.get("aliases", [])))
    item["usage"] = list(dict.fromkeys(item.get("usage", [])))
    item["added_at"] = item.get("added_at") or now
    item["updated_at"] = now
    item.setdefault("image_url", None)
    item.setdefault("thumbnail_url", None)
    item.setdefault("image_refs", [])
    item.setdefault("source_url", item.get("bilibili_url"))
    item.setdefault("summary", item.get("title", ""))
    item = enrich_with_bilibili(item, episodes_by_bvid)
    item = apply_screenshot_candidate(item, screenshot_candidates)
    if item.get("item_type") == "meme" and not item.get("image_url"):
        card_path = f"assets/cards/{item['id']}.svg"
        card_url = repository_asset_url(card_path)
        item["image_url"] = card_url
        item["thumbnail_url"] = item.get("thumbnail_url") or card_url
        item["image_status"] = item.get("image_status") or "generated_card"
        item.setdefault("image_refs", [])
        if not any(ref.get("url") == card_url for ref in item["image_refs"]):
            item["image_refs"].append(
                {
                    "kind": "generated_card",
                    "status": "repo_owned",
                    "path": card_path,
                    "url": card_url,
                    "note": "仓库生成的文字梗图卡，不是视频截图。"
                }
            )
    item["search_text"] = " ".join(
        [
            item.get("title", ""),
            item.get("summary", ""),
            " ".join(item.get("aliases", [])),
            " ".join(item.get("tags", [])),
            " ".join(item.get("tone", [])),
            " ".join(item.get("usage", [])),
            item.get("episode_title") or "",
        ]
    )
    return item


def load_curated_items(
    config: dict[str, Any],
    episodes_by_bvid: dict[str, dict[str, Any]],
    screenshot_candidates: dict[str, dict[str, Any]],
    now: str,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for source in config.get("sources", []):
        if source.get("type") != "curated_json":
            continue
        source_path = ROOT / source["file"]
        payload = load_json(source_path, {"items": []})
        for item in payload.get("items", []):
            items.append(normalize_item(item, source["id"], now, episodes_by_bvid, screenshot_candidates))
    return items


def load_episode_reference_items(config: dict[str, Any], now: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for source in config.get("sources", []):
        if source.get("type") != "bilibili_season_reference":
            continue
        if not source.get("enabled", True):
            continue
        payload = load_json(ROOT / source["file"], {"episodes": [], "series": {}})
        series = payload.get("series", {})
        for episode in payload.get("episodes", []):
            bvid = episode.get("bvid")
            if not bvid:
                continue
            title = episode.get("title") or f"Episode {episode.get('episode')}"
            item = {
                "id": f"xsg-source-video-{bvid}",
                "schema": SCHEMA,
                "source": source["id"],
                "item_type": "source_episode",
                "title": title,
                "summary": f"吃蛋挞的折棒《{series.get('title', source.get('series_title', '吐槽新三国'))}》第 {episode.get('episode')} 期视频来源。",
                "tags": ["新三国", "折棒", "视频来源"],
                "tone": ["source"],
                "language": "zh",
                "safe": True,
                "image_url": None,
                "thumbnail_url": episode.get("cover_url"),
                "source_url": episode.get("url") or bvid_url(bvid),
                "bilibili_url": episode.get("url") or bvid_url(bvid),
                "primary_bvid": bvid,
                "episode": episode.get("episode"),
                "episode_title": title,
                "episode_pubdate": episode.get("pubdate"),
                "episode_stats": episode.get("stat"),
                "image_refs": [
                    {
                        "kind": "bilibili_cover",
                        "status": "reference_only",
                        "url": episode.get("cover_url"),
                        "note": "Bilibili video cover URL; not rehosted by this repository."
                    }
                ] if episode.get("cover_url") else [],
                "added_at": now,
                "updated_at": now,
            }
            item["search_text"] = " ".join([item["title"], item["summary"], " ".join(item["tags"])])
            items.append(item)
    return items


def matches_pack(item: dict[str, Any], rule: dict[str, Any]) -> bool:
    tags_any = set(unique_strings(list(rule.get("tags_any", []))))
    if tags_any:
        item_tags = set(unique_strings(list(item.get("tags", []))))
        if not item_tags.intersection(tags_any):
            return False

    item_types = set(rule.get("item_types", []))
    if item_types and item.get("item_type") not in item_types:
        return False

    return True


def sort_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def key(item: dict[str, Any]) -> tuple[int, str]:
        type_rank = {
            "meme": 0,
            "source_episode": 1,
        }.get(item.get("item_type"), 9)
        return (type_rank, item.get("id", ""))

    return sorted(items, key=key)


def build_index(config_path: Path, index_path: Path, packs_dir: Path, series_path: Path) -> int:
    config = load_json(config_path, {})
    now = utc_now()
    episodes_by_bvid = load_bilibili_episode_map(series_path)
    screenshot_candidates = load_screenshot_candidate_map(ROOT / "data" / "screenshot-candidates.json")

    items = load_curated_items(config, episodes_by_bvid, screenshot_candidates, now)
    items.extend(load_episode_reference_items(config, now))
    items = sort_items(items)[: int(config.get("max_items", 1000))]

    index = {
        "schema": SCHEMA,
        "project": config.get("project", {}),
        "updated_at": now,
        "source_count": len(config.get("sources", [])),
        "item_count": len(items),
        "items": items,
    }
    write_json(index_path, index)

    for pack_name, rule in config.get("packs", {}).items():
        pack_items = [item for item in items if matches_pack(item, rule)]
        pack = {
            "schema": SCHEMA,
            "project": config.get("project", {}),
            "updated_at": now,
            "pack": pack_name,
            "item_count": len(pack_items),
            "items": pack_items,
        }
        write_json(packs_dir / f"{pack_name}.json", pack)

    return len(items)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the New Three Kingdoms meme index.")
    parser.add_argument("--config", default=str(ROOT / "sources.json"))
    parser.add_argument("--index", default=str(ROOT / "index.json"))
    parser.add_argument("--packs-dir", default=str(ROOT / "packs"))
    parser.add_argument("--series", default=str(ROOT / "data" / "bilibili-series.json"))
    args = parser.parse_args()

    count = build_index(
        config_path=Path(args.config),
        index_path=Path(args.index),
        packs_dir=Path(args.packs_dir),
        series_path=Path(args.series),
    )
    print(f"Built {count} New Three Kingdoms index items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
