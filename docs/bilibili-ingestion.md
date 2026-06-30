# Bilibili 采集说明

本仓库以《新三国》梗条目为主，不做 B 站视频搬运。

## 已自动同步的内容

`scripts/update_bilibili_series.py` 会通过 B 站公开接口读取折棒《吐槽新三国》合集元数据，并写入：

```text
data/bilibili-series.json
```

保存内容包括：

```text
BVID
标题
集数
封面 URL
视频 URL
播放/弹幕/评论/点赞等统计信息
```

它不会下载：

```text
视频文件
视频帧
弹幕正文
评论正文
```

## 评论区候选

`scripts/collect_bilibili_candidates.py` 用来做很小规模的评论区候选统计。

默认配置：

```text
data/bilibili-comment-targets.json
data/comment-lexicon.json
```

当前评论抽样目标是 57 个代表视频。脚本只保存聚合候选；如果 B 站接口临时失败，会保留已有统计，不会把旧数据清空。

运行：

```bash
python scripts/collect_bilibili_candidates.py --max-pages 1 --page-size 20
```

输出：

```text
data/comment-candidates.json
```

它只保存关键词命中次数，不保存大量评论原文。

## 视频标题候选

`scripts/mine_title_candidates.py` 会从折棒系列视频标题里提取看起来像梗的短句，并写入：

```text
data/title-candidates.json
```

这些条目会进入主索引，但会标记为 `curation_status: title_mined`，意思是“标题挖掘候选”，后续仍然建议人工复核。

## 文字梗图卡

`scripts/generate_meme_cards.py` 会给 `item_type: meme` 的条目生成 SVG 文字卡：

```text
assets/cards/*.svg
```

这些卡片是仓库生成的原创文字图，不是 B 站视频截图。

## 截图授权候选

`scripts/update_screenshot_candidates.py` 会给一批明确梗生成截图授权候选清单：

```text
data/screenshot-candidates.json
```

它只保存 BVID、出处、建议截图画面和 B 站预览帧雪碧图 URL，不下载、不提交视频帧。

授权流程见：

```text
docs/screenshot-authorization.md
```

## 梗图怎么补

不要批量截取视频画面提交进仓库。

推荐流程：

1. 在 `data/xin-sanguo-memes.json` 里先建梗条目。
2. 填 `primary_bvid` 和 `source_url`。
3. 如果已经确认具体片段，在 `image_refs` 里补时间点说明。
4. 如果有可公开使用的授权图片 URL，再填 `image_url`。
5. 运行 `python scripts/update_index.py` 重新生成索引。

## 为什么这么做

这样做可以让 skills 找到梗和出处，同时避免把视频画面、评论原文、版权素材批量搬进仓库。
