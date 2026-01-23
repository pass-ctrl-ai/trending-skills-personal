"""
HTML Reporter - 生成 HTML 邮件报告
"""
from typing import Dict, List


class HTMLReporter:
    """生成 HTML 邮件报告"""

    def __init__(self):
        """初始化"""
        pass

    def generate_email_html(self, trends: Dict, date: str) -> str:
        """
        生成完整的 HTML 邮件

        Args:
            trends: 趋势数据
            date: 日期

        Returns:
            HTML 字符串
        """
        html_parts = []

        # HTML 头部
        html_parts.append(self._get_header(date))

        # Top 20 榜单
        html_parts.append(self._render_top_20(trends.get("top_20", [])))

        # 上升 Top 5
        html_parts.append(self._render_rising_top5(trends.get("rising_top5", [])))

        # 下降 Top 5
        html_parts.append(self._render_falling_top5(trends.get("falling_top5", [])))

        # 新晋/掉榜
        html_parts.append(self._render_new_dropped(
            trends.get("new_entries", []),
            trends.get("dropped_entries", [])
        ))

        # 暴涨告警
        surging = trends.get("surging", [])
        if surging:
            html_parts.append(self._render_surging(surging))

        # HTML 尾部
        html_parts.append(self._get_footer(date))

        return "\n".join(html_parts)

    def _get_header(self, date: str) -> str:
        """生成 HTML 头部"""
        return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Skills Trending Daily</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .header p {{
            margin: 5px 0 0;
            opacity: 0.9;
        }}
        .section {{
            padding: 20px;
            border-bottom: 1px solid #f0f0f0;
        }}
        .section:last-child {{
            border-bottom: none;
        }}
        .section h2 {{
            margin: 0 0 15px;
            font-size: 18px;
            color: #333;
        }}
        .skill-card {{
            border-left: 4px solid #667eea;
            padding: 12px 15px;
            margin-bottom: 12px;
            background-color: #fafafa;
            border-radius: 0 8px 8px 0;
        }}
        .skill-card:last-child {{
            margin-bottom: 0;
        }}
        .skill-header {{
            display: flex;
            align-items: center;
            margin-bottom: 6px;
        }}
        .skill-rank {{
            font-weight: bold;
            color: #667eea;
            min-width: 30px;
        }}
        .skill-name {{
            font-weight: 600;
            color: #333;
            flex-grow: 1;
        }}
        .skill-meta {{
            font-size: 12px;
            color: #888;
        }}
        .skill-summary {{
            color: #555;
            font-size: 14px;
            line-height: 1.5;
            margin-bottom: 6px;
        }}
        .skill-details {{
            font-size: 13px;
            color: #666;
        }}
        .rank-up {{
            color: #10b981;
        }}
        .rank-down {{
            color: #ef4444;
        }}
        .rank-same {{
            color: #9ca3af;
        }}
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            margin-right: 5px;
            margin-bottom: 3px;
        }}
        .badge-category {{
            background-color: #e5e7eb;
            color: #374151;
        }}
        .badge-new {{
            background-color: #10b981;
            color: white;
        }}
        .badge-alert {{
            background-color: #ef4444;
            color: white;
        }}
        .solves-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
        }}
        .solve-tag {{
            background-color: #f0f0f0;
            color: #555;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 11px;
        }}
        .compact-card {{
            padding: 10px 12px;
            margin-bottom: 8px;
            background-color: #fafafa;
            border-radius: 6px;
            display: flex;
            align-items: center;
        }}
        .compact-card:last-child {{
            margin-bottom: 0;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            font-size: 12px;
            color: #888;
        }}
        .footer a {{
            color: #667eea;
            text-decoration: none;
        }}
        .empty {{
            text-align: center;
            color: #888;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Skills Trending Daily</h1>
            <p>""" + date + """</p>
        </div>"""

    def _get_footer(self, date: str) -> str:
        """生成 HTML 尾部"""
        return """        <div class="footer">
            <p>Powered by <a href="https://skills.sh/trending">Skills Trending</a></p>
            <p style="margin-top:5px;font-size:11px;color:#aaa;">数据来源: skills.sh/trending</p>
        </div>
    </div>
</body>
</html>"""

    def _render_top_20(self, skills: List[Dict]) -> str:
        """渲染 Top 20 榜单"""
        if not skills:
            return self._section_html("📌 Top 20 榜单", '<p class="empty">暂无数据</p>')

        cards = []
        for skill in skills[:20]:
            cards.append(self._format_skill_card(skill, show_details=True))

        return self._section_html("📌 Top 20 榜单", "\n".join(cards))

    def _render_rising_top5(self, skills: List[Dict]) -> str:
        """渲染上升 Top 5"""
        if not skills:
            return ""

        cards = []
        for skill in skills:
            rank_delta = skill.get("rank_delta", 0)
            cards.append(f"""
            <div class="compact-card">
                <span style="min-width:80px;font-weight:bold;">#{skill.get('rank')}</span>
                <span style="flex-grow:1;">{skill.get('name')}</span>
                <span class="rank-up">↑ {rank_delta}</span>
            </div>""")

            if skill.get("summary"):
                cards.append(f"""
            <div style="padding:0 12px 10px;margin-top:-5px;font-size:13px;color:#666;">
                {skill.get('summary')}
            </div>""")

        return self._section_html("📈 上升幅度 Top 5", "\n".join(cards))

    def _render_falling_top5(self, skills: List[Dict]) -> str:
        """渲染下降 Top 5"""
        if not skills:
            return ""

        cards = []
        for skill in skills:
            rank_delta = skill.get("rank_delta", 0)
            cards.append(f"""
            <div class="compact-card">
                <span style="min-width:80px;font-weight:bold;">#{skill.get('rank')}</span>
                <span style="flex-grow:1;">{skill.get('name')}</span>
                <span class="rank-down">↓ {abs(rank_delta)}</span>
            </div>""")

            if skill.get("summary"):
                cards.append(f"""
            <div style="padding:0 12px 10px;margin-top:-5px;font-size:13px;color:#666;">
                {skill.get('summary')}
            </div>""")

        return self._section_html("📉 下降幅度 Top 5", "\n".join(cards))

    def _render_new_dropped(self, new_entries: List[Dict], dropped: List[Dict]) -> str:
        """渲染新晋/掉榜"""
        if not new_entries and not dropped:
            return ""

        html = ""

        # 新晋
        if new_entries:
            new_items = []
            for skill in new_entries:
                new_items.append(f"""
            <div class="compact-card">
                <span class="badge badge-new">🆕 NEW</span>
                <span style="font-weight:bold;">#{skill.get('rank')}</span>
                <span style="flex-grow:1;">{skill.get('name')}</span>
                <span style="color:#888;">{skill.get('installs', 0)}</span>
            </div>""")

                if skill.get("summary"):
                    new_items.append(f"""
            <div style="padding:0 12px 10px;margin-top:-5px;font-size:13px;color:#666;">
                {skill.get('summary')}
            </div>""")

            html += "<h3 style='margin:15px 0 10px;font-size:14px;'>🆕 新晋榜单</h3>"
            html += "\n".join(new_items)

        # 掉榜
        if dropped:
            dropped_items = []
            for skill in dropped[:10]:
                dropped_items.append(f"""
            <div class="compact-card" style="background:#fef5f5;">
                <span class="badge badge-alert">❌</span>
                <span style="font-weight:bold;">#{skill.get('yesterday_rank')}</span>
                <span style="flex-grow:1;">{skill.get('name')}</span>
            </div>""")

            html += "<h3 style='margin:15px 0 10px;font-size:14px;'>❌ 跌出榜单</h3>"
            html += "\n".join(dropped_items)

        return self._section_html("🆕 新晋 / ❌ 跌出", html)

    def _render_surging(self, skills: List[Dict]) -> str:
        """渲染暴涨告警"""
        if not skills:
            return ""

        cards = []
        for skill in skills:
            rate = skill.get("installs_rate", 0)
            installs = skill.get("installs", 0)
            delta = skill.get("installs_delta", 0)

            cards.append(f"""
            <div class="compact-card" style="background:#fef3c7;">
                <span class="badge badge-alert">⚡ +{int(rate*100)}%</span>
                <span style="font-weight:bold;">{skill.get('name')}</span>
                <span style="color:#888;">{delta} → {installs}</span>
            </div>""")

            if skill.get("summary"):
                cards.append(f"""
            <div style="padding:0 12px 10px;margin-top:-5px;font-size:13px;color:#666;">
                {skill.get('summary')}
            </div>""")

        return self._section_html("⚡ 安装量暴涨", "\n".join(cards))

    def _format_skill_card(self, skill: Dict, show_details: bool = True) -> str:
        """格式化单个技能卡片"""
        rank = skill.get("rank", 0)
        name = skill.get("name", "")
        rank_delta = skill.get("rank_delta", 0)
        installs = skill.get("installs", 0)
        installs_delta = skill.get("installs_delta", 0)

        # 排名变化指示
        if rank_delta > 0:
            rank_indicator = f'<span class="rank-up">↑{rank_delta}</span>'
        elif rank_delta < 0:
            rank_indicator = f'<span class="rank-down">↓{abs(rank_delta)}</span>'
        else:
            rank_indicator = '<span class="rank-same">-</span>'

        # 安装量变化
        if installs_delta > 0:
            installs_str = f'{installs:,} <span class="rank-up">(+{installs_delta:,})</span>'
        elif installs_delta < 0:
            installs_str = f'{installs:,} <span class="rank-down">({installs_delta:,})</span>'
        else:
            installs_str = f'{installs:,}'

        # 分类标签
        category_badge = ""
        if skill.get("category_zh"):
            category_badge = f'<span class="badge badge-category">{skill.get("category_zh")}</span>'

        # 解决的问题标签
        solves_html = ""
        if show_details and skill.get("solves"):
            solves_tags = [f'<span class="solve-tag">{s}</span>' for s in skill.get("solves", [])[:5]]
            solves_html = f'<div class="solves-list">{"".join(solves_tags)}</div>'

        # 详细信息
        details_html = ""
        if show_details:
            description = skill.get("description", "")
            use_case = skill.get("use_case", "")

            detail_lines = []
            if description:
                detail_lines.append(f'<p style="margin:5px 0;color:#555;font-size:13px;">{description}</p>')
            if use_case:
                detail_lines.append(f'<p style="margin:5px 0;color:#888;font-size:12px;">💡 {use_case}</p>')

            details_html = "\n".join(detail_lines)

        return f"""        <div class="skill-card">
            <div class="skill-header">
                <span class="skill-rank">#{rank}</span>
                <span class="skill-name">{name}</span>
                {rank_indicator}
            </div>
            <div class="skill-meta">
                {category_badge}
                {installs_str} 安装
            </div>
            <div style="margin:8px 0;">
                {solves_html}
            </div>
            {details_html}
        </div>"""

    def _section_html(self, title: str, content: str) -> str:
        """生成一个完整的 section"""
        return f"""        <div class="section">
            <h2>{title}</h2>
            {content}
        </div>"""


def generate_email_html(trends: Dict, date: str) -> str:
    """便捷函数：生成邮件 HTML"""
    reporter = HTMLReporter()
    return reporter.generate_email_html(trends, date)
