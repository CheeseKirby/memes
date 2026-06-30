#!/usr/bin/env python3
"""Mine meme-like candidate phrases from Zhebang episode titles.

The output is intentionally marked as title-mined candidates. These entries are
useful for search and later human review, but they should not be treated as
fully verified classic memes without curation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


STOP_PHRASES = {
    "登场",
    "开局",
    "这剧里",
    "原来",
    "果然",
    "恭喜你",
}


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


def normalize(value: str) -> str:
    return re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "", value).lower()


def title_tail(title: str) -> str:
    if "：" in title:
        return title.split("：", 1)[1]
    if ":" in title:
        return title.split(":", 1)[1]
    return title


def split_phrases(text: str) -> list[str]:
    text = re.sub(r"新三国(?:re)?\d*", "", text)
    pieces = [text]
    pieces.extend(re.split(r"[，,。！？!?；;、：:]", text))

    result: list[str] = []
    for piece in pieces:
        phrase = piece.strip(" -_，,。！？!?；;、：:")
        phrase = re.sub(r"\s+", "", phrase)
        if not re.search(r"[\u4e00-\u9fff]", phrase):
            continue
        if len(phrase) < 4 or len(phrase) > 24:
            continue
        if phrase in result:
            continue
        if phrase in STOP_PHRASES:
            continue
        result.append(phrase)
    return result


def infer_tags(phrase: str) -> list[str]:
    tags = ["新三国", "折棒", "标题挖掘", "候选梗"]
    if re.search(r"曹操|刘备|关羽|张飞|诸葛亮|司马懿|陈宫|董卓|吕布|华雄|袁绍|孙权|周瑜|赵云|王允", phrase):
        tags.extend(["人物梗", "角色梗"])
    if re.search(r"天意|新三学|理论|历史|时光|真相|定律|宇宙", phrase):
        tags.extend(["世界观", "理论梗"])
    if re.search(r"不可能|恭喜|什么|怎么|为何|谁|啊|吗", phrase):
        tags.extend(["回复", "反应图"])
    if re.search(r"称帝|篡魏|起义|三国|魏|蜀|吴|汉|史", phrase):
        tags.append("历史梗")
    if re.search(r"发癫|抽疯|变态|疯|厚颜无耻", phrase):
        tags.extend(["发癫", "吐槽"])
    return list(dict.fromkeys(tags))


def infer_tone(phrase: str) -> list[str]:
    tone = ["吐槽"]
    if re.search(r"不可能|怎么|为何|谁|吗|？", phrase):
        tone.append("疑惑")
    if re.search(r"发癫|抽疯|疯|变态|厚颜无耻", phrase):
        tone.append("失控")
    if re.search(r"真相|理论|历史|新三学|天意", phrase):
        tone.append("一本正经")
    if re.search(r"恭喜|未来|光明", phrase):
        tone.append("反讽")
    return list(dict.fromkeys(tone))


def score_phrase(phrase: str, episode: dict[str, Any]) -> int:
    score = len(phrase)
    if re.search(r"曹操|刘备|关羽|司马懿|诸葛亮|陈宫|董卓|华雄|王允", phrase):
        score += 8
    if re.search(r"天意|新三学|理论|历史|真相|不可能|厚颜无耻|发癫|抽疯|称帝|未来", phrase):
        score += 10
    if re.search(r"怎么|为何|谁|吗|啊|！|？", phrase):
        score += 4
    stat = episode.get("stat") or {}
    view = int(stat.get("view") or 0)
    like = int(stat.get("like") or 0)
    if view > 2_000_000:
        score += 5
    if like > 50_000:
        score += 5
    return score


def curated_norms(path: Path) -> set[str]:
    payload = load_json(path, {"items": []})
    norms: set[str] = set()
    for item in payload.get("items", []):
        values = [item.get("title", ""), *item.get("aliases", [])]
        for value in values:
            token = normalize(value)
            if token:
                norms.add(token)
    return norms


def is_duplicate(phrase: str, norms: set[str]) -> bool:
    token = normalize(phrase)
    if not token:
        return True
    for existing in norms:
        if len(existing) >= 4 and (existing in token or token in existing):
            return True
    return False


def candidate_id(bvid: str, phrase: str) -> str:
    digest = hashlib.sha1(f"{bvid}:{phrase}".encode("utf-8")).hexdigest()[:10]
    return f"xsg-title-{digest}"


def build_candidates(series_path: Path, curated_path: Path, output_path: Path, max_items: int) -> int:
    series = load_json(series_path, {"episodes": []})
    norms = curated_norms(curated_path)
    raw_candidates: list[tuple[int, dict[str, Any]]] = []

    for episode in series.get("episodes", []):
        bvid = episode.get("bvid")
        if not bvid:
            continue
        for phrase in split_phrases(title_tail(episode.get("title", ""))):
            if is_duplicate(phrase, norms):
                continue
            score = score_phrase(phrase, episode)
            item = {
                "id": candidate_id(bvid, phrase),
                "title": phrase,
                "item_type": "meme",
                "summary": f"从吃蛋挞的折棒《吐槽新三国》第 {episode.get('episode') or '?'} 期标题中挖掘出的候选梗：{phrase}",
                "aliases": [],
                "tags": infer_tags(phrase),
                "tone": infer_tone(phrase),
                "language": "zh",
                "safe": True,
                "usage": ["作为新三国语境下的吐槽短句", "需要人工复核后可提升为正式梗条目"],
                "primary_bvid": bvid,
                "source_url": episode.get("url"),
                "source_kind": "bilibili_title_candidate",
                "curation_status": "title_mined",
                "candidate_score": score,
                "image_status": "generated_card",
            }
            raw_candidates.append((score, item))

    raw_candidates.sort(key=lambda pair: (pair[0], pair[1]["title"]), reverse=True)
    items = [item for _, item in raw_candidates[:max_items]]
    write_json(
        output_path,
        {
            "schema": "https://github.com/CheeseKirby/memes/schema/title-candidates/v1",
            "notes": [
                "这些是从折棒系列视频标题自动挖出的候选梗。",
                "它们会进入主索引用于检索，但仍建议人工复核后再视为正式经典梗。"
            ],
            "item_count": len(items),
            "items": items,
        },
    )
    return len(items)


def main() -> int:
    parser = argparse.ArgumentParser(description="Mine title candidates from Bilibili series metadata.")
    parser.add_argument("--series", default=str(ROOT / "data" / "bilibili-series.json"))
    parser.add_argument("--curated", default=str(ROOT / "data" / "xin-sanguo-memes.json"))
    parser.add_argument("--output", default=str(ROOT / "data" / "title-candidates.json"))
    parser.add_argument("--max-items", type=int, default=180)
    args = parser.parse_args()

    count = build_candidates(Path(args.series), Path(args.curated), Path(args.output), args.max_items)
    print(f"Wrote {count} title-mined candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
