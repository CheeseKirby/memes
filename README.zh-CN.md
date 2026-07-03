# 新三国专属梗库

这是一个给 skills / agents 调用的 **新三国梗索引库**。

重点内容来自中文互联网近年的《新三国》梗，主要参考 B 站 UP 主 **吃蛋挞的折棒** 的《三国杀up锐评新三国 / 吐槽新三国》系列。

## 这个库现在存什么

```text
1. 新三国梗条目
2. 折棒系列视频出处
3. 从标题和评论区挖出的候选梗
4. 一批明确梗的截图
5. 没有截图时使用的 SVG 文字梗图卡
```

每个梗条目主要包含：

```text
梗名
别名
解释
标签
语气
适用场景
来源链接
B 站 BVID
图片 URL
```

## 当前内容

```text
总条目：561
梗条目：264
折棒视频来源：297
已配真实截图：33
当前索引用 SVG 兜底：231
仓库保留 SVG 文字卡：264
```

说明：

```text
33 个比较明确的梗已经配了 assets/screenshots/ 里的截图。
其他 231 个梗条目现在用 assets/cards/ 里的 SVG 文字卡兜底。
```

## 在线查看

可视化浏览页：

```text
https://cheesekirby.github.io/memes/
```

skills 推荐读取：

```text
https://raw.githubusercontent.com/CheeseKirby/memes/main/index.json
```

## 主要文件

```text
index.json
```

主索引。skills 主要读这个。

```text
data/xin-sanguo-memes.json
```

人工整理的新三国梗底稿。以后新增正式梗主要改这里。

```text
data/bilibili-series.json
```

折棒《吐槽新三国》系列视频来源数据，包含 BVID、标题、封面、播放数据等。

```text
data/title-candidates.json
```

从折棒系列视频标题里自动挖出的候选梗。

```text
data/comment-candidates.json
```

评论区候选梗统计。只保存关键词命中次数，不保存大量评论原文。

```text
data/screenshot-candidates.json
```

明确梗的截图来源清单，记录 BVID、建议画面和 B 站预览帧网格。

```text
data/screenshot-selections.json
```

自动裁图时选中的预览帧格子，方便以后人工换更准的截图。

```text
assets/screenshots/
```

已经入库的真实梗截图。

```text
assets/cards/
```

自动生成的 SVG 文字卡。没有真实截图时用它兜底。

## 分包

```text
packs/worldview.json          世界观梗，比如天意、定律类
packs/quotes.json             台词梗、短句梗
packs/characters.json         人物梗、角色梗
packs/episodes.json           折棒视频来源
packs/reaction.json           可当回复/反应图用的梗
packs/title-candidates.json   从标题挖出的候选梗
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
episode_title
```

例如用户要：

```text
找一个表示“剧情太离谱，只能说是天意”的梗
```

skill 应该匹配到：

```text
天意
```

如果条目有 `image_url`，就可以直接返回图片。

如果 `image_status` 是 `screenshot`，说明图片来自 `assets/screenshots/`。

如果图片来自 `assets/cards/`，说明它是 SVG 文字卡兜底。

## 怎么更新

每日 GitHub Actions 会自动运行：

```bash
python scripts/update_bilibili_series.py
python scripts/mine_title_candidates.py
python scripts/update_screenshot_candidates.py
python scripts/update_index.py
python scripts/generate_meme_cards.py
```

作用：

```text
刷新折棒视频列表
重新挖标题候选梗
刷新截图来源清单
重新生成 index.json 和 packs/*.json
重新生成 SVG 文字卡
```

手动重新生成截图：

```bash
python scripts/generate_screenshots.py --overwrite
python scripts/update_index.py
```

## 怎么继续扩充

新增正式梗，主要改：

```text
data/xin-sanguo-memes.json
```

新增截图来源，主要改：

```text
data/screenshot-targets.json
```

然后运行：

```bash
python scripts/update_screenshot_candidates.py
python scripts/generate_screenshots.py --overwrite
python scripts/update_index.py
python scripts/generate_meme_cards.py
```

## 一句话总结

这个仓库现在是：

```text
新三国梗目录
+ 折棒视频出处库
+ 候选梗挖掘结果
+ 少量明确梗截图
+ SVG 文字卡兜底
```
