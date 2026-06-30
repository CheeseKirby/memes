# 新三国梗图截图授权流程

这个仓库可以逐步把丑丑的 SVG 文字卡换成真实截图，但前提是先拿到授权。

## 现在有什么

```text
data/screenshot-targets.json
```

人工挑出来的明确梗，说明应该去哪个视频找图、适合截什么画面。

```text
data/screenshot-candidates.json
```

脚本生成的授权候选清单。每条包含：

```text
梗 ID
梗名
BVID
视频出处
建议截图画面
B 站预览帧雪碧图 URL
授权状态
授权后图片应放的仓库路径
```

## 重要原则

授权前不要把视频帧提交进仓库。

授权前只保存：

```text
BVID
视频链接
截图建议
B 站预览帧引用
```

授权后再保存：

```text
assets/screenshots/<item_id>.jpg
```

## 怎么找图

1. 打开 `data/screenshot-candidates.json`。
2. 找到想补图的梗。
3. 打开 `storyboard.image_urls[0]`。
4. 这是一张 B 站视频预览帧雪碧图，不是最终图片。
5. 按 `frame_hint` 找最像梗图的一格。
6. 去原视频确认具体画面。
7. 向 UP 主申请授权。

## 授权建议问法

可以这样问：

```text
您好，我在做一个开源的新三国梗索引库，主要用于让 AI skills / agents 查询梗名、出处和用法。

想申请授权使用您《吐槽新三国》系列中的若干单帧截图，作为对应梗条目的配图。

使用方式：
- 放在 GitHub 仓库 assets/screenshots/ 目录
- 在 README、可视化浏览页、skills 返回结果中展示
- 标注来源视频链接和 UP 主
- 不下载或搬运视频，不批量保存评论

如果可以，我会只使用经过人工挑选的少量单帧截图。
```

## 授权后怎么入库

拿到授权后：

1. 把截图放到：

```text
assets/screenshots/<item_id>.jpg
```

2. 修改 `data/screenshot-targets.json` 里对应条目：

```json
"authorization_status": "authorized_for_repository"
```

3. 运行：

```bash
python scripts/update_screenshot_candidates.py
python scripts/update_index.py
```

4. 对应梗的 `image_url` 就会从 SVG 文字卡换成授权截图。

## 本地临时图放哪

未授权的本地截图可以临时放：

```text
assets/pending-authorization/
```

这个目录已经被 `.gitignore` 忽略，不会提交到 GitHub。
