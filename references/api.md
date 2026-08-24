# Vidiohalo Agent API

Base URL: `https://vidiohalo.com/api`

All Agent endpoints require a paid Vidiohalo plan and `Authorization: Bearer ${VIDIOHALO_AGENT_KEY}`. Eligible users create and revoke this credential in **个人中心 → Agent**; Free accounts do not see this entry and cannot create or use a Key. A Key can create billable tasks using that user's point balance. Full plaintext is returned only once and is never stored by Vidiohalo.

## Assets

`GET /agent/v1/assets` lists reusable assets. Use ready assets whose MIME type matches the requested role: image for person/product, audio for voice, video for remake source or B-roll.

`POST /agent/v1/assets/upload` accepts multipart form data with binary `file` and `rights_confirmed=true`. Upload first, then pass the returned `id` into a creation request.

## Unified creation endpoint

`POST /agent/v1/creations` uses `workflow` as a discriminator.

### One-click talking video

```json
{
  "workflow": "oneclick",
  "script": "完整口播文案",
  "requirements": "可选的视觉与表达要求",
  "resolution": "720P",
  "aspect_ratio": "9:16",
  "person_asset_ids": ["asset_..."],
  "voice_asset_ids": ["asset_..."],
  "product_asset_ids": [],
  "broll_asset_ids": [],
  "tts_speaker": "zh_male_taocheng_uranus_bigtts",
  "speech_rate": 0
}
```

Resolution values are `720P` and `2K`. Aspect ratios are `21:9`, `16:9`, `4:3`, `1:1`, `3:4`, and `9:16`. Speech rate ranges from `-50` to `100`.

### Viral remake

```json
{
  "workflow": "remake",
  "source_kind": "url",
  "source_platform": "douyin",
  "source_url": "full copied share text containing https://...",
  "requirements": "保留镜头节奏，更换人物和对白",
  "person_asset_ids": [],
  "product_asset_ids": [],
  "audio_asset_ids": [],
  "resolution": "720P",
  "aspect_ratio": "source"
}
```

For an asset source, use `source_kind=asset`, `source_platform=direct`, and `source_asset_id`. Supported URL platforms are `direct`, `wechat`, `douyin`, `xiaohongshu`, `kuaishou`, and `bilibili`.

Resolution values are `720P` and `2K` for both workflows.

## Response and status

The response contains `id`, `workflow`, `status`, relative `detail_url`, and `created_at`. Query `GET /agent/v1/creations/{id}`. Prefix `job_` is one-click and `remake_` is viral remake. Terminal statuses are `completed`, `failed`, and `canceled`.

## Errors

- `400`: invalid source, material, duration/plan violation, or malformed request.
- `401`: missing Agent Key.
- `403`: invalid/revoked Agent Key, or an account without an eligible paid plan.
- `402`: insufficient points.
- `413`/`415`: upload size/type problem.
- `429`: rate limit; wait before retrying.
- `5xx`: service/provider failure. Query an already returned task ID before considering another create request.
