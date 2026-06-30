# 新三国专属梗库

这个仓库现在已经改成 **新三国专属梗库**。

它不再追求覆盖所有 meme，而是专门收集中文互联网近年的《新三国》相关梗，重点参考 B 站 UP 主 **吃蛋挞的折棒** 的《三国杀up锐评新三国 / 吐槽新三国》系列。

## 这个库现在存什么

现在主要存三类东西：

```text
1. 新三国梗条目
2. 折棒 B 站视频来源
3. 评论区候选梗统计
```

它不是大图床，不会把 B 站视频截图批量搬进仓库。

每个梗条目会存：

```text
梗名
别名
解释
标签
语气
适用场景
来源链接
B站视频 BVID
截图/梗图状态
```

比如：

```json
{
  "title": "天意",
  "summary": "用于解释新三国剧情突然拐弯、人物突然被安排、历史线被强行拨动的核心世界观梗。",
  "tags": ["新三国", "折棒", "世界观", "理论梗", "天意学"],
  "image_status": "needs_curated_image"
}
```

## 现在有多少东西

当前生成结果是：

```text
总条目：561
梗条目：264
折棒视频来源：297
```

也就是说，现在不是 325 张图，而是：

```text
84 个已整理的新三国梗
180 个从视频标题挖出的候选梗
297 个折棒系列视频来源
264 张仓库生成的原创 SVG 文字梗图卡
```

## 主要文件

```text
index.json
```

主索引。skills 主要读它。

```text
data/xin-sanguo-memes.json
```

人工整理的新三国梗底稿。以后新增梗主要改这里。

```text
data/bilibili-series.json
```

从 B 站接口同步的折棒《吐槽新三国》系列视频来源。里面有 BVID、标题、封面、播放数据等。

```text
data/comment-candidates.json
```

评论区候选梗统计。目前只保存关键词命中次数，不保存大量评论原文。

```text
data/title-candidates.json
```

从折棒系列视频标题中自动挖出的候选梗。

```text
assets/cards/
```

仓库自动生成的原创 SVG 文字梗图卡。它们不是 B 站视频截图。

```text
sources.json
```

说明这个库现在的数据来源和分类规则。

```text
scripts/update_bilibili_series.py
```

同步折棒 B 站合集信息。

```text
scripts/update_index.py
```

根据人工梗底稿和 B 站视频来源生成 `index.json`。

```text
scripts/mine_title_candidates.py
```

从折棒系列视频标题里挖候选梗。

```text
scripts/generate_meme_cards.py
```

给梗条目生成原创 SVG 文字梗图卡。

```text
scripts/collect_bilibili_candidates.py
```

抽样统计评论区候选梗。它只统计配置好的词有没有出现，不批量保存评论。

## 分类文件

现在的分包是：

```text
packs/worldview.json    世界观梗，比如天意、定律类，当前 23 条
packs/quotes.json       台词梗、短句梗，当前 11 条
packs/characters.json   人物梗、角色梗，当前 85 条
packs/episodes.json     折棒视频来源，当前 297 条
packs/reaction.json     可当回复/反应图用的梗，当前 90 条
packs/title-candidates.json  从视频标题自动挖出的候选梗，当前 180 条
```

## skill 怎么用

skill 读取这个地址：

```text
https://raw.githubusercontent.com/CheeseKirby/memes/main/index.json
```

然后按用户意思找：

```text
title
summary
aliases
tags
tone
usage
```

比如用户要：

```text
找一个表示“剧情太离谱，只能说是天意”的梗
```

skill 就应该匹配到：

```text
天意
```

如果用户要：

```text
找一个“不可能接受这个结果”的回复梗
```

skill 就可能匹配到：

```text
不可能，绝对不可能
```

## 关于梗图

目前很多条目还没有真正的 `image_url`。

原因是：

```text
不能直接把 B 站视频画面批量下载后放进仓库
```

所以现在的做法是：

```text
先存梗
再存出处
再标记截图状态
以后人工补授权图或可用图
```

相关字段：

```text
image_url       真正可用的梗图 URL，如果有
thumbnail_url   B站封面或预览图
image_status    这条梗图现在是什么状态
image_refs      图片引用来源
primary_bvid    主要参考视频
source_url      来源链接
```

常见状态：

```text
needs_curated_image   需要人工补图
video_frame_needed    需要从视频片段确认截图
reference_only        只有来源参考，不当作梗图本体
```

## 每天怎么更新

GitHub Actions 每天会运行：

```bash
python scripts/update_bilibili_series.py
python scripts/mine_title_candidates.py
python scripts/update_index.py
python scripts/generate_meme_cards.py
```

作用是：

```text
刷新折棒视频列表
重新生成 index.json
重新生成 packs/*.json
```

评论区候选提取不会默认每天跑，因为它需要更谨慎。

要手动跑评论候选统计：

```bash
python scripts/collect_bilibili_candidates.py --max-pages 1 --page-size 20
```

## 怎么继续扩充

以后新增梗，主要改：

```text
data/xin-sanguo-memes.json
```

新增一条类似：

```json
{
  "id": "xsg-quote-example",
  "title": "梗名",
  "summary": "这个梗是什么意思",
  "aliases": ["别名"],
  "tags": ["新三国", "折棒", "台词梗"],
  "tone": ["吐槽"],
  "language": "zh",
  "safe": true,
  "usage": ["适合什么场景"],
  "primary_bvid": "BVxxxx",
  "source_url": "https://www.bilibili.com/video/BVxxxx",
  "image_status": "video_frame_needed"
}
```

然后运行：

```bash
python scripts/update_index.py
```

## 一句话总结

这个仓库现在是：

```text
新三国梗目录
+ 折棒视频出处库
+ 评论区候选梗统计工具
```

不是：

```text
泛 meme 图库
大规模截图仓库
B站视频搬运仓库
```
