# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- ( upcoming changes )

---

## [1.0.0] - 2026-01-23

### 首次发布

**Skills Trending Daily** - 自动追踪 skills.sh 技能排行榜，AI 智能分析，每日趋势报告邮件

### 核心功能

- **skills.sh 榜单抓取**
  - 每天自动获取 Top 100 技能排行榜
  - 支持从 HTML 和内联 JSON 解析数据
  - 智能解析安装量（支持 "5.6K" 格式）

- **Top 20 详情抓取**
  - 深度抓取技能详情页
  - 提取 "When to use" 和规则列表
  - 2秒请求限速，避免服务器压力

- **Claude AI 智能分析**
  - 批量总结和分类 Top 20 技能
  - 提取摘要、描述、使用场景
  - 智能分类（12 种分类）
  - 提取解决的问题标签

- **趋势计算引擎**
  - 排名变化计算（上升/下降）
  - 安装量变化率计算
  - 新晋榜单检测
  - 跌出榜单检测
  - 暴涨告警（>30% 阈值）

- **SQLite 数据存储**
  - 3 张表：skills_daily、skills_details、skills_history
  - 30 天数据自动保留
  - 支持趋势查询和统计

- **HTML 邮件报告**
  - 精美的响应式邮件模板
  - Top 20 榜单（带 AI 总结）
  - 上升/下降 Top 5
  - 新晋/掉榜展示
  - 暴涨告警高亮

- **Resend 邮件发送**
  - 可靠的邮件发送服务
  - 支持 HTML 邮件

- **Claude Code Skill**
  - trending-skills Skill
  - 自然语言查询支持
  - 今日榜单查询
  - 技能详情查询
  - 趋势分析查询

### 技术栈

- Python 3.11+
- SQLite（数据存储）
- Claude API（AI 分析）
- Resend（邮件服务）
- BeautifulSoup4（HTML 解析）

### GitHub Actions

- 每天 UTC 02:00（北京时间 10:00）自动运行
- 支持手动触发
- 数据库自动备份（90天保留）

### 文件结构

```
skills-trending/
├── .github/workflows/
│   └── skills-trending.yml    # GitHub Actions 配置
├── plugins/
│   └── trending-skills/       # Claude Code Skill
│       └── skills/trending-skills/
│           └── SKILL.md
├── src/
│   ├── config.py
│   ├── database.py
│   ├── skills_fetcher.py
│   ├── detail_fetcher.py
│   ├── claude_summarizer.py
│   ├── trend_analyzer.py
│   ├── html_reporter.py
│   ├── resend_sender.py
│   └── main_trending.py
├── requirements.txt
├── .env.example
├── CHANGELOG.md
└── README.md
```

### 环境变量

```bash
# Claude API
ZHIPU_API_KEY=xxx
ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic

# Resend 邮件
RESEND_API_KEY=xxx
EMAIL_TO=your@email.com
RESEND_FROM_EMAIL=onboarding@resend.dev

# 数据库
DB_PATH=data/trends.db
DB_RETENTION_DAYS=30

# 告警阈值
SURGE_THRESHOLD=0.3
```

---

[Unreleased]: https://github.com/yourusername/skills-trending/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/yourusername/skills-trending/releases/tag/v1.0.0
