# Skills Trending Daily

自动追踪 <https://skills.sh/trending> 技能排行榜，抓取技能详情并做 AI 分类/总结，计算趋势并通过 Telegram 推送（GitHub Actions 每 3 天一次）。

## 项目要点（最新实现）

- **去重抓取**：当检测到「今日 Top20 与上一期 Top20 完全一致」时，会改为从榜单中挑选**未出现在上一期 Top20**的前 20 个技能，避免重复分析。
- **Telegram 默认推送**：发送 HTML parse_mode 文本。
- **AI（OpenAI-compatible）**：默认使用 **NVIDIA NIM integrate**。
  - 默认 `OPENAI_BASE_URL=https://integrate.api.nvidia.com/v1`
  - 你当前使用模型：`meta/llama3-70b-instruct`
- **AI 状态可见**：Telegram 报告顶部会显示 `AI: <model> | ok x/y | fallback z`。

## 快速开始（本地）

```bash
git clone https://github.com/pass-ctrl-ai/trending-skills-personal.git
cd trending-skills-personal

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY / OPENAI_MODEL / TELEGRAM_* 等

python src/main_trending.py
```

## 配置（环境变量）

必需：

- `OPENAI_API_KEY`：NVIDIA NIM 的 nvapi key（或任何 OpenAI-compatible 的 key）
- `OPENAI_MODEL`：例如 `meta/llama3-70b-instruct`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

可选：

- `OPENAI_BASE_URL`：覆盖默认 NIM（默认已内置：`https://integrate.api.nvidia.com/v1`）
- `TELEGRAM_MESSAGE_THREAD_ID`：话题群 thread id
- `NOTIFY_CHANNEL`：`telegram`（默认）或 `resend`
- `RESEND_API_KEY` / `EMAIL_TO` / `RESEND_FROM_EMAIL`：仅当你切到 `resend` 时需要
- `DB_PATH`（默认 `data/trends.db`）
- `DB_RETENTION_DAYS`（默认 30）

## GitHub Actions

1. Fork/复制本仓库
2. Settings → Secrets and variables → Actions → Secrets 配置：
   - `OPENAI_API_KEY`
   - `OPENAI_MODEL`（建议：`meta/llama3-70b-instruct`）
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
3. 启用 Actions

默认计划任务：每 **3 天** UTC 02:00 运行（见 `.github/workflows/skills-trending.yml`）。

## License

MIT
