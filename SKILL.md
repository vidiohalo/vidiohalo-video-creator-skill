---
name: vidiohalo-video-creator
description: Create Vidiohalo one-click talking videos or viral remakes through natural-language conversation. Use when a user wants to turn a script into a talking video, remake a reference or social video, upload/select Vidiohalo assets, start a billable generation, or check its progress.
---

# Vidiohalo Video Creator

Create a Vidiohalo task by collecting intent conversationally, then calling `scripts/vidiohalo.py`. Read [references/api.md](references/api.md) only when exact fields, platform values, or error behavior are needed.

## Authentication

Require a paid Vidiohalo plan and `VIDIOHALO_AGENT_KEY` in the environment. Free accounts cannot create or use Agent Keys. If the key is missing, direct an eligible user to **Vidiohalo → 个人中心 → Agent** to create a Key, then ask them to configure it as an environment variable. Never ask the user to paste the Key into chat, print it, store it in files, or place it in command arguments.

Use `VIDIOHALO_API_BASE_URL` only for a non-production deployment; otherwise the script defaults to `https://vidiohalo.com/api`.

## Conversation flow

1. Determine whether the user wants `oneclick` (一键口播) or `remake` (爆款复刻).
2. Collect only missing required information.
3. Resolve materials:
   - Run `list-assets` to reuse existing Vidiohalo assets.
   - For a local file, first confirm the user owns or is authorized to use it, then run `upload --rights-confirmed`.
4. Summarize the script/instructions, references, resolution, and aspect ratio before submission. State clearly that starting generation consumes account points.
5. Submit once after the user confirms. Do not automatically retry a create request whose response is unknown; query status first to avoid duplicate billable tasks.
6. Return the task ID and full Vidiohalo detail URL. Use `status` for later updates.

## One-click talking video

Require:

- Complete spoken script.
- At least one person image asset or authorized public person-image URL.

Ask optionally for voice reference, product images, B-roll, speech speed, resolution (`720P` or `2K`), and aspect ratio. Defaults are `720P`, `9:16`, and normal speech speed.

Do not treat a voice reference as a timing audio track; it is the target IP voice reference. The service creates its own TTS timing preview internally.

Example:

```bash
python3 scripts/vidiohalo.py create-oneclick \
  --script "完整口播文案" \
  --person asset_123 \
  --voice asset_456 \
  --resolution 720P \
  --aspect-ratio 9:16
```

## Viral remake

Require:

- Exactly one reference source: an existing video asset, public video URL, or supported social-platform share text/link.
- Clear instructions describing what to change and what to preserve.

Supported social platforms: `douyin`, `xiaohongshu`, `kuaishou`, `wechat`, and `bilibili`. Pass the full copied share text; the service extracts the URL.

Person, product, and audio references are optional. Defaults are `720P`, source aspect ratio, and automatic remake planning.

Example:

```bash
python3 scripts/vidiohalo.py create-remake \
  --source-url "复制的完整分享文字 https://v.douyin.com/example/" \
  --platform douyin \
  --requirements "保留镜头节奏，把人物换成橘猫，所有对白改成东北话" \
  --resolution 720P
```

## Guardrails

- Never submit copyrighted, private, or identity-sensitive material without explicit user authorization.
- Do not invent asset IDs. List or upload assets first.
- Do not expose provider names, internal prompts, profit multipliers, or internal resolution aliases.
- Do not claim completion until `status` reports `completed`.
- For `401`, stop and ask the user to configure their Agent Key. For `403`, report the API message: the Key may be invalid/revoked, or the account may need a paid plan.
- For insufficient points, link the user to `https://vidiohalo.com/pricing`; do not alter the request to evade billing.
