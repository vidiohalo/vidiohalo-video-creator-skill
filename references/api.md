# Vidiohalo Agent API

Base URLs: CN `https://vidiohalo.com/api`; Global `https://videohalo.ai/api`. Set `VIDIOHALO_API_BASE_URL` to the site owning the key and assets.

All Agent endpoints require a Vidiohalo account and `Authorization: Bearer ${VIDIOHALO_AGENT_KEY}`. Free and paid users can create and revoke this credential in **个人中心 → Agent**. A Key can create billable tasks using that user's point balance. Full plaintext is returned only once and is never stored by Vidiohalo.

## Balance

`GET /agent/v1/balance` returns the account identified by the Agent Key; it accepts no user ID. It is non-billable and creates no task. Available on CN and Global.

- `available_points`: points available to spend now.
- `held_points`: points reserved by unfinished work, excluded from the available balance.
- `monthly_points_remaining`, `topup_points_remaining`: plan allowance and additional-point balances.
- `plan_id`, `subscription_status`, `current_period_end`, `monthly_expires_at`: plan status and expiry information; dates may be null.

All point values are already display units. No user session cookie is needed. Missing, invalid or revoked keys are rejected. A fresh query reflects the same expiry handling as the web wallet.

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
- `403`: invalid or revoked Agent Key.
- `402`: insufficient points.
- `413`/`415`: upload size/type problem.
- `429`: rate limit; wait before retrying.
- `5xx`: service/provider failure. Query an already returned task ID before considering another create request.

## Current workflow boundaries

- `create-oneclick --voice-id ID` forwards a known stock or ready cloned voice ID as `tts_speaker`. `--voice` forwards a reference asset, not an original soundtrack. `--speaker male|female` remains a legacy CN shortcut.
- Original recordings, confirmed preview soundtracks and optional caption-calibration scripts are attached through the Talking Video page. The Agent schema has no fields for those attachments.
- Agent remake creation maps to `auto_generate=false`. `analysis_ready` requires continuing on the returned project page. Web-created projects may enable automatic generation after analysis.
- AI director conversations use session-authenticated web endpoints. Agent Keys only authorize the documented `/agent/v1/` API.
- Status exposes the task state and detail link. When blocked or waiting for input, inspect the existing project for the specific reason and resolve it there.
- Covers, publishing copy, subtitle editing/SRT export and clip regeneration are available from the web delivery page. They have no commands in this client.
- Do not hard-code points-per-second or free-credit offers. Use the selected site's pricing and actual task quote. CN one-off plans and Global subscriptions have different billing terms.
