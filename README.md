# CheeseKirby Meme Index

An online meme index for skills and agents.

The repository stores lightweight meme metadata: title, tags, language, tone,
source, and image URL. The first version does not mirror large image files, so
the repo stays cheap and easy to share.

## Public Endpoints

Use this endpoint from skills:

```text
https://raw.githubusercontent.com/CheeseKirby/memes/main/index.json
```

If GitHub Pages is enabled for the repository, this endpoint will also work:

```text
https://cheesekirby.github.io/memes/index.json
```

Pack endpoints:

```text
https://raw.githubusercontent.com/CheeseKirby/memes/main/packs/coding.json
https://raw.githubusercontent.com/CheeseKirby/memes/main/packs/reaction.json
https://raw.githubusercontent.com/CheeseKirby/memes/main/packs/zh.json
https://raw.githubusercontent.com/CheeseKirby/memes/main/packs/en.json
```

## Skill Usage

When a skill needs a meme:

1. Fetch `index.json`.
2. Filter by `safe`, `language`, `tags`, or `tone`.
3. Match the user intent against `title`, `tags`, `tone`, and `summary`.
4. Return the selected item's `image_url` and keep `source_url` for attribution.

Minimal item shape:

```json
{
  "id": "reddit_programmerhumor_t3_example",
  "title": "When the build passes on the first try",
  "summary": "A programming meme suitable for coding success reactions.",
  "tags": ["coding", "programming", "developer"],
  "tone": ["reaction", "humor"],
  "language": "en",
  "safe": true,
  "image_url": "https://example.com/meme.jpg",
  "thumbnail_url": "https://example.com/meme.jpg",
  "source_url": "https://reddit.com/r/ProgrammerHumor/comments/example",
  "source": "reddit_programmerhumor",
  "score": 1200,
  "created_at": "2026-06-29T00:00:00Z",
  "added_at": "2026-06-29T00:00:00Z"
}
```

## Daily Updates

GitHub Actions runs `scripts/update_index.py` every day. It reads
`sources.json`, discovers new public meme image URLs, updates `index.json`,
and regenerates files in `packs/`.

Run it manually:

```bash
python scripts/update_index.py
```

## Add Sources

Edit `sources.json`. Keep sources public, low-volume, and respectful of each
site's rules.

The current updater supports Reddit JSON listing URLs:

```json
{
  "id": "reddit_programmerhumor",
  "type": "reddit_json",
  "url": "https://www.reddit.com/r/ProgrammerHumor/top.json?t=day&limit=50",
  "default_tags": ["coding", "programming", "developer", "meme"],
  "tone": ["humor", "reaction"],
  "language": "en",
  "safe": true,
  "min_score": 100
}
```

## GitHub Pages

The repository includes `.github/workflows/pages.yml`, which deploys the
static browser viewer when GitHub Pages is available for the repository.

If the Pages URL is still 404, open the repository settings once:

1. Open repository settings on GitHub.
2. Go to **Pages**.
3. Select **GitHub Actions** as the source.
5. Save.

After that, open:

```text
https://cheesekirby.github.io/memes/
```
