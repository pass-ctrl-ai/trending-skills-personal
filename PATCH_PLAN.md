# PATCH PLAN — trending-skills（个人化改造 / 你的 Fork）

> 目标：把 `geekjourneyx/trending-skills` 改造成适合你自己使用的版本，并最终推送到你自己的 GitHub 仓库。

## 0) 快速现状
- 上游仓库：https://github.com/geekjourneyx/trending-skills
- 语言：Python 3.11+
- 关键能力：抓取 skills.sh/trending → 抓 TopN 详情 → LLM 总结分类 → SQLite 记录历史 → 生成 HTML 邮件 → Resend 发送

---

## 1) 你要的“个人化”目标（先填需求）
- [ ] 目标1：
- [ ] 目标2：
- [ ] 目标3：

建议你明确：
- 你想追踪哪些来源？仅 skills.sh 还是要加其它榜单？
- 邮件内容你最在意哪部分？Top20 摘要/上升下降/新晋掉榜/暴涨告警
- AI 分析希望输出什么结构？（更短/更细/更偏学习路线/更偏工具对比）

---

## 2) 仓库策略（推荐：Fork + upstream）
### 方案 A：Fork（推荐）
优点：后续可同步上游更新。

步骤：
1. 在 GitHub 上 fork 上游仓库到你的账号
2. 本地（本项目目录）设置远端：

```bash
# 在项目根目录
# 先看当前远端

git remote -v

# 把 origin 改成你自己的仓库（示例）
git remote set-url origin git@github.com:<YOUR_GH_NAME>/trending-skills.git

# 添加 upstream 指向原作者仓库
git remote add upstream https://github.com/geekjourneyx/trending-skills.git

# 拉取上游更新
git fetch upstream
```

### 方案 B：新建你自己的仓库（不保留 upstream）
适合你想完全重构、减少历史包袱。

---

## 3) 开发环境（本地运行）
```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -U pip
pip install -r requirements.txt

playwright install chromium
```

运行：
```bash
python src/main_trending.py
```

---

## 4) 配置与密钥（绝不提交到仓库）
### 环境变量（README 提到）
- `ZHIPU_API_KEY`（Claude 兼容代理的 key）
- `ANTHROPIC_BASE_URL`（可选，默认 https://open.bigmodel.cn/api/anthropic）
- `RESEND_API_KEY`
- `EMAIL_TO`
- `RESEND_FROM_EMAIL`（可选）

建议做法：
- 本地：复制 `.env.example` → `.env`，用 dotenv 或 shell export 注入
- Actions：全部放 GitHub Secrets
- 确保 `.env` 在 `.gitignore`（检查/补充）

---

## 5) 改动清单（TODO）

### 5.1 抓取层（skills_fetcher/detail_fetcher）
- [ ] 抓取 TopN 可配置（Top20/Top50）
- [ ] 更稳的解析方式（不要只依赖 `innerText` + 正则；可考虑定位 DOM 节点）
- [ ] 增加缓存/失败重试策略与更清晰的日志

### 5.2 AI 分析层（claude_summarizer）
- [ ] 统一输出 JSON schema（summary / description / use_case / solves / category / tags）
- [ ] 限制 token 和温度，保证可复现性
- [ ] 为“学习项目”定制：输出「推荐学习路径/关键概念/同类替代」

### 5.3 趋势层（trend_analyzer + db）
- [ ] 明确“暴涨”阈值定义，并在报告中解释原因
- [ ] 增加周趋势/月趋势摘要

### 5.4 报告层（html_reporter + resend_sender）
- [ ] HTML 模板个人化：标题、配色、模块排序
- [ ] 每个技能增加「一键跳转 skills.sh + GitHub repo」

### 5.5 工程化（质量与安全）
- [ ] requirements 改成锁版本（pip-tools/uv/poetry 任一）
- [ ] 增加 lint/format（ruff/black）
- [ ] 增加 secrets 检查（gitleaks / trufflehog）

---

## 6) 提交与发布规范
- 分支建议：
  - `main` 保持可运行
  - `feature/<topic>` 开发
- Commit message：`feat:` / `fix:` / `chore:` / `docs:`

---

## 7) 验收标准（Definition of Done）
- [ ] 本地可跑通：能生成 HTML（即使不发邮件）
- [ ] Secrets 不会出现在日志/邮件里
- [ ] Actions 定时跑通（如启用）
- [ ] 邮件内容符合你的个人化需求
