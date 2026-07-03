# Skill 接入说明

这个仓库现在是 **新三国专属梗索引库**。

skill 不需要自己去网上乱搜新三国梗，只需要读取这个公开 JSON：

```text
https://raw.githubusercontent.com/CheeseKirby/memes/main/index.json
```

## 基本规则

当 skill 需要一个《新三国》相关梗时：

1. 下载 `index.json`。
2. 只使用 `safe: true` 的条目。
3. 优先使用 `item_type: meme` 的条目。
4. 用用户意图匹配 `title`、`summary`、`aliases`、`tags`、`tone`、`usage`。
5. `source_episode` 条目只当作视频出处，不要当成梗本体。
6. 优先返回 `image_status: screenshot` 的真实截图；其他条目可以返回 SVG 文字卡。

## 重要字段

```text
id             条目 ID
item_type      条目类型，meme 表示梗，source_episode 表示视频来源
title          梗名或视频标题
summary        简短解释
aliases        别名
tags           标签
tone           语气
usage          适用场景
language       语言，目前主要是 zh
safe           是否适合默认公开调用
image_url      整理好的梗图 URL
thumbnail_url  B 站封面或预览图，可能为空
source_url     来源链接
primary_bvid   B 站视频 ID
image_status   梗图整理状态
```

注意：`assets/screenshots/*.jpg` 是真实截图；`assets/cards/*.svg` 是仓库生成的文字卡兜底。

## 推荐检索方式

把用户需求和这些字段拼在一起做匹配：

```text
title
summary
aliases
tags
tone
usage
episode_title
```

例如用户说：

```text
找一个表示“剧情太离谱，只能说是天意”的梗
```

应该匹配：

```text
天意
```

例如用户说：

```text
找一个表示“我不接受这个结果”的回复梗
```

可能匹配：

```text
不可能，绝对不可能
```

## 返回结果建议

如果条目有 `image_url`：

```json
{
  "title": "天意",
  "summary": "用于解释新三国剧情突然拐弯、人物突然被安排、历史线被强行拨动的核心世界观梗。",
  "image_url": "https://example.com/image.jpg",
  "source_url": "https://example.com/source"
}
```

如果条目是 SVG 文字卡：

```json
{
  "title": "天意",
  "summary": "用于解释新三国剧情突然拐弯、人物突然被安排、历史线被强行拨动的核心世界观梗。",
  "image_status": "generated_card",
  "image_url": "https://raw.githubusercontent.com/CheeseKirby/memes/main/assets/cards/xsg-worldview-tianyi.svg",
  "primary_bvid": "BVxxxx"
}
```

## 不要做的事

不要让 skill：

```text
把 source_episode 当成梗图
忽略 safe 字段
把评论区原文大规模复制进输出
```

## 最小实现逻辑

```python
def score(item, query):
    text = " ".join([
        item.get("title", ""),
        item.get("summary", ""),
        " ".join(item.get("aliases", [])),
        " ".join(item.get("tags", [])),
        " ".join(item.get("tone", [])),
        " ".join(item.get("usage", [])),
        item.get("episode_title") or "",
    ]).lower()

    return sum(1 for word in query.lower().split() if word in text)
```

## 一句话

skill 查这个库时，应该把它当成：

```text
新三国梗名 + 解释 + 来源 + 图片 的索引
```

而不是：

```text
一个已经存满图片的图床
```
