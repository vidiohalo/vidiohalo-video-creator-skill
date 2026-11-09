---
name: vidiohalo-video-creator
description: Create Vidiohalo Talking Video jobs and Viral Remake analyses, select or upload Vidiohalo assets, and check task status. Use for the Vidiohalo Agent API on Global or CN. For a user-requested direct model API experiment, follow the named provider's workflow.
---

# Vidiohalo Video Creator

Create a Vidiohalo task by collecting intent conversationally, then calling `scripts/vidiohalo.py`. Read [references/api.md](references/api.md) only when exact fields, platform values, or error behavior are needed.

## Authentication

Require a Vidiohalo account and `VIDIOHALO_AGENT_KEY` in the environment. Free and paid accounts can create and use Agent Keys. If the key is missing, direct the user to **Vidiohalo → 个人中心 → Agent** to create a Key, then ask them to configure it as an environment variable. Never ask the user to paste the Key into chat, print it, store it in files, or place it in command arguments.

Use the site where the user created their key and assets. The client defaults to CN at `https://vidiohalo.com/api`. For Global, set `VIDIOHALO_API_BASE_URL=https://videohalo.ai/api` for the invocation. If the request includes a Vidiohalo job link, use its site. Keep the same site for asset lookup, creation, and status.

## Conversation flow

1. Determine whether the user wants `oneclick` (一键口播) or `remake` (爆款复刻).
2. Collect only missing required information.
3. Resolve materials:
   - Run `list-assets` to reuse existing Vidiohalo assets.
   - For a local file, first confirm the user owns or is authorized to use it, then run `upload --rights-confirmed`.
4. Summarize the script or instructions, references, output settings, and what the submission starts. Explain that work uses the account's points and plan limits. Confirm before a billable submission unless the user already explicitly approved that exact action.
5. Submit once. If the outcome is unknown, check the returned task ID if available or ask the user to check Jobs on the same site before considering resubmission.
6. Return the task ID, current status, and full Vidiohalo detail URL. Use `status` for updates. If a job is waiting for credits or a user action, report the action instead of continuing to poll.

## One-click talking video

Require:

- Complete spoken script.
- At least one person image asset or authorized public person-image URL.

Ask optionally for the preferred voice, product images, B-roll, speech speed, resolution (`720P` or `2K`), and aspect ratio. Defaults are `720P`, `9:16`, and normal speech speed. For a known stock or ready cloned voice ID from the same site, pass `--voice-id`. A raw `--voice` asset is a timbre reference.

The Agent API derives timing from TTS. If the user wants to use a complete recording or an exact confirmed TTS soundtrack, send them to the same site's Talking Video page to use that workflow. The Agent API accepts a script and voice references and has no fields to attach the confirmed soundtrack or its optional caption calibration script.

Keep the user's spoken wording intact. Natural sentence and clause boundaries help the service plan clips. Let the service choose boundaries within its duration limit. If an original-audio job reports a sync issue, check its existing job page. Eligible clips can be split and recovered automatically. If the page asks for a retry, use the clip-level action there to preserve successful clips.

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

Person, product, and audio references are optional. Defaults are `720P`, source aspect ratio, and automatic remake planning. Creation queues analysis. When status is `analysis_ready`, open the returned remake link to review the plan and confirm generation. If payment is required, direct the user to the same project page.

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
- For `401`, stop and ask the user to configure their Agent Key. For `403`, report that the Key may be invalid or revoked.
- For insufficient points, use the pricing page of the selected site.
- If safety review rejects the request, say “内容未通过安全审核。如有疑问，请联系客服。” or “This content did not pass the safety review. If you have any questions, please contact support.” Use the user's language.

## Direct model experiments

For a request to call an external model directly, use its API and credentials separately from the Vidiohalo workflow. Verify input capabilities and respect the user's duration and spend constraints. See [the xAI notes](references/api.md#direct-xai-tests) for Grok image and audio inputs. Ask before using private Vidiohalo materials with an additional provider when the user has not authorized that transfer.
