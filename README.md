# Skills Trending Daily

自动追踪 <https://skills.sh/trending> 技能排行榜，抓取详情并做 AI 分类/总结，计算趋势并通过 Telegram 推送（GitHub Actions 每 3 天一次）。

## 项目要点（最新实现）

- **去重抓取**：当检测到「今日 Top20 与上一期 Top20 完全一致」时，会改为从榜单中挑选**未出现在上一期 Top20**的前 20 个技能，避免重复分析。
- **Telegram 默认推送**：发送 HTML parse_mode 文本（无邮件依赖）。
- **AI（OpenAI-compatible）**：当前默认走 **NVIDIA NIM integrate**（OpenAI-compatible endpoint）。
  - 代码默认 `OPENAI_BASE_URL=https://integrate.api.nvidia.com/v1`
  - 你现在使用的模型：`meta/llama3-70b-instruct`
- **可观测性**：Telegram 报告顶部会显示 AI 状态（ok/fallback），避免“看起来像 AI 但其实是降级/望文生义”。

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

## 输出说明

- Telegram Top20 每条格式：`rank. name — summary`
- 报告顶部会显示：`AI: <model> | ok x/y | fallback z`

## License

MIT

---

## 配置说明

### 环境变量

| 变量 | 必需 | 说明 | 默认值 |
|-----|------|------|--------|
| `OPENAI_API_KEY` | Yes | OpenAI API Key | - |
| `OPENAI_BASE_URL` | No | OpenAI Base URL（代理/兼容接口可用） | - |
| `OPENAI_MODEL` | No | OpenAI 模型 | `gpt-4o-mini` |
| `NOTIFY_CHANNEL` | No | 通知渠道：`telegram` 或 `resend` | `telegram` |
| `TELEGRAM_BOT_TOKEN` | Yes* | Telegram Bot Token（当 `telegram` 时必填） | - |
| `TELEGRAM_CHAT_ID` | Yes* | Telegram Chat ID（当 `telegram` 时必填） | - |
| `TELEGRAM_MESSAGE_THREAD_ID` | No | 话题群 thread id（可选） | - |
| `RESEND_API_KEY` | Yes* | Resend API Key（当 `resend` 时必填） | - |
| `EMAIL_TO` | Yes* | 收件人邮箱（当 `resend` 时必填） | - |
| `RESEND_FROM_EMAIL` | No | 发件人邮箱 | `onboarding@resend.dev` |
| `DB_PATH` | No | 数据库路径 | `data/trends.db` |
| `DB_RETENTION_DAYS` | No | 数据保留天数 | `30` |
| `SURGE_THRESHOLD` | No | 暴涨阈值（比例） | `0.3` |

### Telegram 配置（推荐）

1. 在 BotFather 创建 bot，拿到 `TELEGRAM_BOT_TOKEN`
2. 把 bot 拉进你要接收消息的群（或私聊 bot）
3. 获取 `TELEGRAM_CHAT_ID`

> 如果你使用“话题群/论坛群”，可选配置 `TELEGRAM_MESSAGE_THREAD_ID`。

### Resend 配置（可选）

1. 注册 [Resend](https://resend.com)
2. 创建 API Key
3. 配置发件人域名（或使用默认的 `onboarding@resend.dev`）

---

## 使用方法

### 命令行运行

```bash
# 完整流程
python src/main_trending.py
```

### 数据库查询

```bash
# 查看最新数据日期
sqlite3 data/trends.db "SELECT date FROM skills_daily ORDER BY date DESC LIMIT 1;"

# 查看今日排行榜 Top 10
sqlite3 data/trends.db "SELECT rank, name, installs FROM skills_daily WHERE date = '2026-01-24' ORDER BY rank LIMIT 10;"

# 查看技能详情
sqlite3 data/trends.db "SELECT name, summary, category FROM skills_details WHERE name = 'remotion-best-practices';"
```

---

## GitHub Actions

### 自动化部署

1. Fork 本仓库
2. 在 GitHub Settings > Secrets and variables > Actions 中添加：
   - `OPENAI_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - （可选）`OPENAI_MODEL`（例如 `gpt-4o-mini`）
3. 启用 Actions

### 定时执行

默认每 **3 天**在 **UTC 02:00** 自动运行（约等于北京时间 10:00）。

修改时间：编辑 `.github/workflows/skills-trending.yml` 中的 `cron` 表达式。

### 手动触发

在 GitHub Actions 页面点击 "Run workflow" 按钮手动执行。

---

## 数据模型

### skills_daily - 每日快照

| 字段 | 类型 | 说明 |
|-----|------|------|
| `id` | INTEGER | 主键 |
| `date` | TEXT | 日期 (YYYY-MM-DD) |
| `rank` | INTEGER | 当日排名 |
| `name` | TEXT | 技能名称 |
| `owner` | TEXT | 拥有者 |
| `installs` | INTEGER | 安装量 |
| `installs_delta` | INTEGER | 安装量变化 |
| `installs_rate` | REAL | 安装量变化率 |
| `rank_delta` | INTEGER | 排名变化（正=上升） |
| `url` | TEXT | 技能链接 |

### skills_details - 技能详情

| 字段 | 类型 | 说明 |
|-----|------|------|
| `id` | INTEGER | 主键 |
| `name` | TEXT | 技能名称（唯一） |
| `summary` | TEXT | AI 一句话摘要 |
| `description` | TEXT | 详细描述 |
| `use_case` | TEXT | 使用场景 |
| `solves` | TEXT | JSON：解决的问题列表 |
| `category` | TEXT | 分类（英文） |
| `category_zh` | TEXT | 分类（中文） |
| `rules_count` | INTEGER | 规则数量 |
| `owner` | TEXT | 拥有者 |
| `url` | TEXT | 技能链接 |

### skills_history - 历史趋势

| 字段 | 类型 | 说明 |
|-----|------|------|
| `id` | INTEGER | 主键 |
| `skill_name` | TEXT | 技能名称 |
| `date` | TEXT | 日期 |
| `rank` | INTEGER | 当日排名 |
| `installs` | INTEGER | 安装量 |

---

## 开发指南

### 项目结构

```
skills-trending/
├── .github/workflows/
│   └── skills-trending.yml    # GitHub Actions 配置
├── src/
│   ├── config.py              # 配置管理
│   ├── database.py            # SQLite 操作
│   ├── skills_fetcher.py      # 榜单抓取（Playwright）
│   ├── detail_fetcher.py      # 详情抓取
│   ├── claude_summarizer.py   # AI 分析
│   ├── trend_analyzer.py      # 趋势计算
│   ├── html_reporter.py       # 邮件生成
│   ├── resend_sender.py       # 邮件发送
│   └── main_trending.py       # 主入口
├── plugins/
│   └── trending-skills/       # Claude Code Skill
├── data/
│   └── trends.db              # 数据库（运行时生成）
├── requirements.txt
├── .env.example
├── CHANGELOG.md
└── README.md
```

### 核心模块说明

| 模块 | 功能 |
|-----|------|
| `skills_fetcher.py` | 使用 Playwright 抓取 skills.sh 榜单，支持动态渲染 |
| `detail_fetcher.py` | 抓取单个技能的详细页面内容 |
| `claude_summarizer.py` | 调用 OpenAI API 分析技能内容（文件名保留兼容） |
| `trend_analyzer.py` | 计算排名变化、新晋/掉榜、暴涨检测 |
| `html_reporter.py` | 生成专业 HTML 邮件（无 emoji，可点击链接） |
| `database.py` | SQLite 数据库操作，支持数据持久化 |

### 扩展开发

**新增数据源**
```python
# 修改 skills_fetcher.py
class SkillsFetcher:
    def __init__(self, timeout: int = 30000):
        self.trending_url = "your_custom_url"
```

**新增分析维度**
```python
# 修改 trend_analyzer.py
def calculate_trends(self, today_skills, today, ai_summary_map):
    # 添加新的分析逻辑
    pass
```

**自定义邮件样式**
```python
# 修改 html_reporter.py
def _get_header(self, date: str) -> str:
    # 修改样式和布局
    pass
```

---

## 常见问题

### 邮件没有收到？

1. 检查 Resend API Key 是否正确
2. 确认收件人邮箱地址
3. 查看垃圾邮件箱
4. 检查 GitHub Actions 日志

### Playwright 浏览器安装失败？

```bash
# 重新安装
playwright install chromium --with-deps
```

### 数据库文件在哪里？

默认位置：`data/trends.db`

### 如何查看历史数据？

```bash
sqlite3 data/trends.db
.tables
SELECT * FROM skills_daily ORDER BY date DESC LIMIT 10;
```

### 如何更改运行时间？

编辑 `.github/workflows/skills-trending.yml`：
```yaml
schedule:
  - cron: '0 2 * * *'  # UTC 时间，每天 02:00
```

---

## 打赏 Buy Me A Coffee

如果该项目帮助了您，请作者喝杯咖啡吧

### WeChat

<img src="https://raw.githubusercontent.com/geekjourneyx/awesome-developer-go-sail/main/docs/assets/wechat-reward-code.jpg" alt="微信打赏码" width="200" />

---

## 作者

- **作者**: `geekjourneyx`
- **X (Twitter)**: https://x.com/seekjourney
- **公众号**: 极客杰尼

关注公众号，获取更多 AI 编程、AI 工具与 AI 出海建站的实战分享：

<p>
<img src="https://raw.githubusercontent.com/geekjourneyx/awesome-developer-go-sail/main/docs/assets/qrcode.jpg" alt="公众号：极客杰尼" width="180" />
</p>

---

## License

[MIT](LICENSE)

---

## 致谢

- [skills.sh](https://skills.sh) - 技能数据来源
- [OpenAI](https://platform.openai.com) - LLM 分析
- [Telegram Bot API](https://core.telegram.org/bots/api) - 消息推送
- [Resend](https://resend.com) - 邮件服务（可选）
- [Playwright](https://playwright.dev) - 浏览器自动化
