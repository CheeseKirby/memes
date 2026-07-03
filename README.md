# 新三国专属梗库

这是一个给 skills / agents 使用的 **新三国梗索引库**。

它专门整理中文互联网近年的《新三国》梗，重点参考 B 站 UP 主 **吃蛋挞的折棒** 的《三国杀up锐评新三国 / 吐槽新三国》系列。

详细说明见：

```text
README.zh-CN.md
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

这个库主要存：

```text
梗名
别名
梗的解释
标签
语气
适用场景
来源链接
B 站 BVID
图片 URL
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

常用分包：

```text
https://raw.githubusercontent.com/CheeseKirby/memes/main/packs/worldview.json
https://raw.githubusercontent.com/CheeseKirby/memes/main/packs/quotes.json
https://raw.githubusercontent.com/CheeseKirby/memes/main/packs/characters.json
https://raw.githubusercontent.com/CheeseKirby/memes/main/packs/episodes.json
https://raw.githubusercontent.com/CheeseKirby/memes/main/packs/reaction.json
```

## 主要文件

```text
index.json                         主索引，skills 主要读这个
data/xin-sanguo-memes.json         人工整理的新三国梗底稿
data/bilibili-series.json          折棒系列视频来源数据
data/title-candidates.json         从视频标题挖出的候选梗
data/comment-candidates.json       评论区候选梗统计
data/screenshot-candidates.json    明确梗的截图来源清单
data/screenshot-selections.json    自动裁图选中的预览帧格子
assets/screenshots/                已入库截图
assets/cards/                      SVG 文字卡兜底
```

## skill 怎么用

skill 读取：

```text
https://raw.githubusercontent.com/CheeseKirby/memes/main/index.json
```

然后按用户意图匹配：

```text
title
summary
aliases
tags
tone
usage
episode_title
```

如果条目有 `image_url`，可以直接返回图片。

常见图片状态：

```text
screenshot       已配真实截图
generated_card   SVG 文字卡
screenshot_target  适合继续补截图
```

## 可视化查看

打开：

```text
https://cheesekirby.github.io/memes/
```

页面可以搜索、筛选、随机查看，也会显示当前有多少条已经配截图。

## 每日更新

GitHub Actions 每天会运行：

```bash
python scripts/update_bilibili_series.py
python scripts/mine_title_candidates.py
python scripts/update_screenshot_candidates.py
python scripts/update_index.py
python scripts/generate_meme_cards.py
```

手动重新生成截图：

```bash
python scripts/generate_screenshots.py --overwrite
python scripts/update_index.py
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
