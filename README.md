# Vidiohalo 智能体技能

把 Vidiohalo 自己开发的智能体技能安装到 WorkBuddy、龙虾（OpenClaw）、Codex 等支持 SKILL.md 的智能体中，结合本地资料、知识库和 AI 工作流创建视频。请先确认所用软件支持安装技能并运行 Python 脚本。

这个仓库是一个可直接安装的 Agent Skill。它会通过 Vidiohalo Agent API：

- 查询和复用你的 Vidiohalo 素材；
- 上传已获授权的图片、音频和视频；
- 创建一键口播视频；
- 从公开视频、素材或社交平台分享文本创建爆款复刻；
- 查询生成进度，并返回 Vidiohalo 任务详情页。

Skill 创建的任务会像网页端任务一样显示在 Vidiohalo 的“任务”页面中，并使用同一个账户的点数和套餐权限。

## 前提条件

- Python 3.10 或更高版本；
- 支持 `SKILL.md` 的 Agent；
- Vidiohalo 账户（Free 和付费套餐均可使用）；
- 一个 Vidiohalo Agent Key。

## 安装

### 方式一：让 Codex 安装

把这个仓库地址发给 Codex，并说：

```text
请安装这个 Skill：https://github.com/vidiohalo/vidiohalo-video-creator-skill
```

### 方式二：手动安装

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/vidiohalo/vidiohalo-video-creator-skill.git \
  ~/.codex/skills/vidiohalo-video-creator
```

安装后重新启动 Codex，或打开一个新任务，让它重新发现 Skill。

如果你的 Agent 使用其他 Skill 目录，把仓库克隆到该 Agent 的 Skill 目录即可。仓库根目录本身就是完整的 Skill。

## 配置 Agent Key

1. 登录 [Vidiohalo](https://vidiohalo.com)。
2. 打开 **个人中心 → Agent**。
3. 创建 Agent Key。完整 Key 只会显示一次，请立即保存到安全的密码管理器。
4. 在运行 Agent 的环境中配置：

```bash
export VIDIOHALO_AGENT_KEY='你的 Agent Key'
```

请勿把 Agent Key 粘贴到聊天、截图、代码、命令行参数或 Git 仓库中。这个 Key 代表你的账户权限，发起视频生成会消耗账户点数。

默认连接 `https://vidiohalo.com/api`。Global 账户请配置 `VIDIOHALO_API_BASE_URL=https://videohalo.ai/api`，素材和 Key 必须属于同一站点。连接本地环境时可配置：

```bash
export VIDIOHALO_API_BASE_URL='http://localhost:8000'
```

## 自然语言使用

安装后可以直接对 Agent 说：

```text
用 Vidiohalo 把这段文案做成 9:16 的一键口播视频，人物使用我素材库里的“品牌主理人”，声音使用“主理人音色”：……
```

```text
用 Vidiohalo 爆款复刻这个抖音分享文本，保留镜头节奏，把人物换成橘猫，所有对白改成东北话：……
```

```text
帮我查看刚才 Vidiohalo 视频的生成进度。
```

Agent 会先收集缺少的信息，展示本次生成的摘要和点数消耗提醒，并在你确认后提交。创建请求是计费操作，Skill 不会在结果未知时盲目重试。

## 命令行使用

Skill 附带一个无第三方依赖的 Python 客户端：

```bash
python3 scripts/vidiohalo.py list-assets
```

上传已授权素材：

```bash
python3 scripts/vidiohalo.py upload ./person.png --rights-confirmed
```

创建一键口播：

```bash
python3 scripts/vidiohalo.py create-oneclick \
  --script '完整口播文案' \
  --person asset_123 \
  --voice asset_456 \
  --resolution 720P \
  --aspect-ratio 9:16
```

创建爆款复刻：

```bash
python3 scripts/vidiohalo.py create-remake \
  --source-url '完整复制的分享文字 https://v.douyin.com/example/' \
  --platform douyin \
  --requirements '保留镜头节奏，把人物换成橘猫，所有对白改成东北话' \
  --resolution 720P
```

查询任务状态：

```bash
python3 scripts/vidiohalo.py status job_xxx
python3 scripts/vidiohalo.py status remake_xxx
```

支持的社交平台包括抖音、小红书、快手、微信视频号和哔哩哔哩。可以直接传入平台复制出来的完整分享文本，Vidiohalo 会提取其中的链接。

## 分析、导演与交付

爆款复刻提交后先分析参考视频。当前技能创建的项目需要打开返回的项目链接查看拆解、可复刻范围和具体阻断原因，再继续生成。可以在项目页与 AI 导演对话、补充资料和调整要求。网页创建的项目可启用分析通过后自动生成。

一键口播支持脚本、参考素材、已有音色 ID 和语速。要使用完整朗读原声或确认过的配音，请进入网页一键口播流程。成片页面可下载视频、生成封面和发布文案、调整字幕并下载 SRT，以及重做支持调整的片段。

手机端从右上角菜单进入任务和个人中心。任务遇到缺资料或点数不足时，继续处理原任务。

## 权限与安全

- 只上传你拥有或已获授权使用的素材；
- 不要用 Skill 处理未经授权的私人、版权或身份敏感内容；
- Agent Key 仅通过环境变量读取，客户端不会把它写入文件；
- 完整 Key 不会出现在正常输出中；
- 如怀疑泄露，请立即在 Vidiohalo **个人中心 → Agent** 停用旧 Key 并创建新 Key。

更多字段和错误码见 [Agent API 参考](references/api.md)。

## 仓库结构

```text
.
├── SKILL.md
├── agents/openai.yaml
├── references/api.md
└── scripts/vidiohalo.py
```

## 开发与验证

```bash
python3 -m py_compile scripts/vidiohalo.py
python3 scripts/vidiohalo.py --help
```

如果本机安装了 Codex 的 `skill-creator` 校验工具，也可以运行其 `quick_validate.py` 验证目录结构和 frontmatter。

## License

[MIT](LICENSE)


## 查询剩余点数

可以直接对智能体说“查一下我还剩多少点”。技能会使用当前站点的 Agent Key 查询余额，不创建任务、不扣点。

```bash
python3 scripts/vidiohalo.py balance
```

返回可用点数、任务冻结点数、套餐与补充点数余额以及到期时间。冻结点数不计入可用余额；不同站点的余额分别查询。
