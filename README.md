# 新三国专属梗库

这是一个给 skills / agents 使用的 **新三国专属梗索引库**。

它专门整理中文互联网近年的《新三国》梗，重点参考 B 站 UP 主 **吃蛋挞的折棒** 的《三国杀up锐评新三国 / 吐槽新三国》系列。

更详细说明见：

```text
README.zh-CN.md
```

## 这个项目是什么

一句话：

```text
这是一个新三国梗目录。
```

它主要存：

```text
梗名
别名
梗的解释
标签
语气
适用场景
来源链接
B 站视频 BVID
截图/梗图状态
```


## 当前内容

当前索引生成结果：

```text
总条目：561
梗条目：264
折棒视频来源：297
```

也就是说，现在库里主要是：

```text
84 个整理过的新三国梗
180 个从视频标题挖出的候选梗
297 个折棒《吐槽新三国》系列视频出处
264 张仓库生成的原创 SVG 文字梗图卡
```

## 在线地址

可视化浏览页：

```text
https://cheesekirby.github.io/memes/
```

skills 推荐读取主索引：

```text
https://raw.githubusercontent.com/CheeseKirby/memes/main/index.json
```

分包索引：

```text
https://raw.githubusercontent.com/CheeseKirby/memes/main/packs/worldview.json
https://raw.githubusercontent.com/CheeseKirby/memes/main/packs/quotes.json
https://raw.githubusercontent.com/CheeseKirby/memes/main/packs/characters.json
https://raw.githubusercontent.com/CheeseKirby/memes/main/packs/episodes.json
https://raw.githubusercontent.com/CheeseKirby/memes/main/packs/reaction.json
```

## 主要文件

```text
index.json
```

主索引，skills 主要读这个。

```text
data/xin-sanguo-memes.json
```

人工整理的新三国梗底稿。以后新增梗主要改这里。

```text
data/bilibili-series.json
```

折棒《吐槽新三国》系列的视频来源数据，包括 BVID、标题、封面、播放数据等。

```text
data/comment-candidates.json
```

评论区候选梗统计。只保存关键词命中次数，不保存大量评论原文。

```text
data/title-candidates.json
```

从折棒系列视频标题中自动挖出的候选梗。

```text
data/screenshot-candidates.json
```

明确梗的截图授权候选清单。只保存出处和预览帧引用，不保存未授权截图。

```text
assets/cards/
```

仓库自动生成的原创 SVG 文字梗图卡，不是视频截图。

```text
scripts/update_bilibili_series.py
```

同步折棒 B 站合集信息。

```text
scripts/update_index.py
```

根据人工梗底稿和 B 站来源生成 `index.json` 和分包。

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

抽样统计评论区候选梗。

```text
scripts/update_screenshot_candidates.py
```

生成截图授权候选清单。授权前不下载、不提交视频帧。

## 分包说明

```text
packs/worldview.json    世界观梗，比如天意、定律类
packs/quotes.json       台词梗、短句梗
packs/characters.json   人物梗、角色梗
packs/episodes.json     折棒视频来源
packs/reaction.json     可当回复/反应图用的梗
packs/title-candidates.json  从视频标题自动挖出的候选梗
```

## skill 怎么用

skill 读取：

```text
https://raw.githubusercontent.com/CheeseKirby/memes/main/index.json
```

然后按用户意图匹配这些字段：

```text
title
summary
aliases
tags
tone
usage
```

例如用户要：

```text
找一个表达“剧情太离谱，只能说是天意”的梗
```

skill 应该匹配到：

```text
天意
```

如果 `image_url` 为空，说明还没有整理好的梗图，只能返回 `source_url`、`thumbnail_url` 或 `primary_bvid` 作为来源参考。

## 梗图状态

很多条目目前没有真正的 `image_url`。

原因是：

```text
不能直接把 B 站视频画面批量下载后塞进仓库。
```

所以当前做法是：

```text
先存梗
再存出处
再标记截图状态
以后人工补授权图或可公开使用的图片 URL
```

常见状态：

```text
needs_curated_image   需要人工补图
video_frame_needed    需要从视频片段确认截图
reference_only        只有来源参考，不当作梗图本体
```

## 每日更新

GitHub Actions 每天运行：

```bash
python scripts/update_bilibili_series.py
python scripts/mine_title_candidates.py
python scripts/update_index.py
python scripts/generate_meme_cards.py
```

作用是：

```text
刷新折棒视频来源
重新生成主索引
重新生成分包索引
```

评论区候选提取不会默认每天跑，因为它更需要人工复核。

手动抽样评论区候选：

```bash
python scripts/collect_bilibili_candidates.py --max-pages 1 --page-size 20
```

## 更多文档

```text
README.zh-CN.md                 详细中文说明
docs/skill-integration.md       skill 接入说明
docs/bilibili-ingestion.md      B 站采集说明
docs/screenshot-authorization.md 截图授权流程
```

## 一句话总结

这个仓库现在是：

```text
新三国梗目录
+ 折棒视频出处库
+ 评论区候选梗统计工具
```

