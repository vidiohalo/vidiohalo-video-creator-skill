# Vidiohalo Agent API

| Site | API base | Pricing |
| --- | --- | --- |
| CN (client default) | `https://vidiohalo.com/api` | [CN pricing](https://vidiohalo.com/pricing) |
| Global | `https://videohalo.ai/api` | [Global pricing](https://videohalo.ai/pricing) |

All Agent endpoints require a Vidiohalo account and `Authorization: Bearer ${VIDIOHALO_AGENT_KEY}`. Free and paid users can create and revoke this credential in **Account → Agent** or **个人中心 → Agent**. Use the key on the site that issued it. A Key can create billable tasks using that user's point balance. Full plaintext is returned only once and is never stored by Vidiohalo.

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
  "speech_rate": 0
}
```

Resolution values are `720P` and `2K`. Aspect ratios are `21:9`, `16:9`, `4:3`, `1:1`, `3:4`, and `9:16`. Speech rate ranges from `-50` to `100`. The account's plan determines the available resolution and duration.

`tts_speaker` is optional. Pass the exact voice ID with `--voice-id` when the user has one from the selected site. Stock IDs use `minimax:` on CN and `eleven:` on Global. A saved, ready clone owned by the account uses `clone:<id>`. Agent asset listing returns media assets, while the website's voice picker shows available voices. The legacy CLI options `--speaker male` and `--speaker female` select CN presets. On Global both legacy values resolve to the site's default stock voice.

The one-click Agent request uses TTS for planning and can include timbre references via `voice_asset_ids`. Use the website for a full narration recording, caption calibration, a confirmed TTS soundtrack, or clip retry. The Agent endpoint does not expose those inputs or actions.

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

Resolution values are `720P` and `2K` for both workflows. Remake creation starts at `analysis_queued`. `analysis_ready` means the plan is ready for review and generation confirmation on the project page. `analysis_payment_required` and `generation_payment_required` also require action on that page.

## Response and status

The response contains `id`, `workflow`, `status`, relative `detail_url`, and `created_at`. Query `GET /agent/v1/creations/{id}`. Prefix `job_` is one-click and `remake_` is viral remake. Terminal statuses are `completed`, `failed`, and `canceled`.

## Errors

- `400`: invalid source, material, duration/plan violation, or malformed request.
- `401`: missing Agent Key.
- `403`: invalid or revoked Agent Key.
- `402`: insufficient points.
- `413`/`415`: upload size/type problem.
- `422`: request fields failed validation.
- `429`: rate limit; wait before retrying.
- `5xx`: service/provider failure. Query an already returned task ID before considering another create request.

For a safety rejection, use the localized support message from [the skill](../SKILL.md#guardrails).

## Direct xAI tests

For a direct xAI experiment, check the current [xAI model capability table](https://docs.x.ai/developers/model-capabilities/video/overview#capabilities-and-specifications). `grok-imagine-video-1.5-lite` takes a single starting frame via `image`. The separate `reference_images` mode and preset voice references are available on `grok-imagine-video-1.5`. The [reference audio documentation](https://docs.x.ai/developers/model-capabilities/video/reference-to-video#reference-audio) describes custom voice files as a partner feature. Voice reference and driving lip movements from a supplied waveform are distinct capabilities.

If the user accepts replacing the soundtrack after generation, use the requested TTS audio as the delivered audio track and describe the result as post-aligned. Keep the source video stream when the user wants the original composition and burned-in subtitles.
