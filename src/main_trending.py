#!/usr/bin/env python3
"""
Skills Trending 主入口
自动获取 skills.sh 技能排行榜，AI 分析，生成趋势报告并发送邮件
"""
import sys
import os
from datetime import datetime, timezone

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.config import (
    OPENAI_API_KEY,
    NOTIFY_CHANNEL,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    TELEGRAM_MESSAGE_THREAD_ID,
    RESEND_API_KEY,
    EMAIL_TO,
    RESEND_FROM_EMAIL,
    DB_PATH,
    DB_RETENTION_DAYS,
    TOP_N_DETAILS,
)
from src.skills_fetcher import SkillsFetcher
from src.detail_fetcher import DetailFetcher
from src.claude_summarizer import ClaudeSummarizer
from src.database import Database
from src.trend_analyzer import TrendAnalyzer
from src.html_reporter import HTMLReporter
from src.resend_sender import ResendSender
from src.telegram_sender import TelegramSender


def print_banner():
    """打印程序横幅"""
    banner = """
╔════════════════════════════════════════════════════════════╗
║                                                              ║
║   Skills Trending Daily - 技能趋势追踪系统                   ║
║                                                              ║
║   自动获取 skills.sh 排行榜 · AI 智能分析                    ║
║   趋势计算 · HTML 邮件报告 · Resend 发送                    ║
║                                                              ║
╚════════════════════════════════════════════════════════════╝
"""
    print(banner)


def get_today_date() -> str:
    """获取今日日期 YYYY-MM-DD"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def main():
    """主函数"""
    print_banner()

    # 检查环境变量
    if not OPENAI_API_KEY:
        print("❌ 错误: OPENAI_API_KEY 环境变量未设置")
        sys.exit(1)

    # 通知渠道检查
    if NOTIFY_CHANNEL == "telegram":
        if not TELEGRAM_BOT_TOKEN:
            print("❌ 错误: TELEGRAM_BOT_TOKEN 环境变量未设置")
            sys.exit(1)
        if not TELEGRAM_CHAT_ID:
            print("❌ 错误: TELEGRAM_CHAT_ID 环境变量未设置")
            sys.exit(1)
    elif NOTIFY_CHANNEL == "resend":
        if not RESEND_API_KEY:
            print("❌ 错误: RESEND_API_KEY 环境变量未设置")
            sys.exit(1)
        if not EMAIL_TO:
            print("❌ 错误: EMAIL_TO 环境变量未设置")
            sys.exit(1)
    else:
        print(f"❌ 错误: NOTIFY_CHANNEL 不支持: {NOTIFY_CHANNEL} (仅支持 telegram/resend)")
        sys.exit(1)

    # 获取今日日期
    today = get_today_date()
    print(f"[目标日期] {today}")
    print(f"   (北京时间: {datetime.now(timezone.utc)} + 8h)")
    print()

    try:
        # 1. 获取今日榜单
        print(f"[步骤 1/7] 获取技能排行榜...")
        fetcher = SkillsFetcher()
        today_skills = fetcher.fetch()
        print(f"   成功获取 {len(today_skills)} 个技能")
        print()

        # 2. 初始化数据库（用于去重判断 & 保存结果）
        print(f"[步骤 2/7] 初始化数据库...")
        db = Database(DB_PATH)
        db.init_db()

        # 3. 选择需要抓取详情的 TopN（去重逻辑）
        print(f"[步骤 3/7] 选择需要抓取详情的 Top {TOP_N_DETAILS} ...")
        detail_candidates = today_skills[:TOP_N_DETAILS]

        latest_date = db.get_latest_date()
        # latest_date 可能就是今天（如果重复运行）；仅当 latest_date 存在且与 today 不同才做对比
        if latest_date and latest_date != today:
            prev_top = db.get_top_n_names(latest_date, n=TOP_N_DETAILS)
            curr_top = [s.get("name") for s in today_skills[:TOP_N_DETAILS]]

            # 判断是否“前20固定”（顺序完全一致）
            if prev_top and curr_top == prev_top:
                print(f"   ⚠️ 检测到今日 Top{TOP_N_DETAILS} 与上次({latest_date})完全一致，启用去重抓取逻辑")
                prev_set = set(prev_top)
                dedup = [s for s in today_skills if s.get("name") not in prev_set]
                if len(dedup) >= TOP_N_DETAILS:
                    detail_candidates = dedup[:TOP_N_DETAILS]
                    print(f"   ✅ 改为抓取榜单中未出现在上一期 Top{TOP_N_DETAILS} 的 {TOP_N_DETAILS} 个技能")
                else:
                    print(f"   ⚠️ 去重后不足 {TOP_N_DETAILS} 个，回退抓取原 Top{TOP_N_DETAILS}")

        # 4. 抓取 Top N 详情
        print(f"[步骤 4/7] 抓取 Top {TOP_N_DETAILS} 详情...")
        detail_fetcher = DetailFetcher()
        top_details = detail_fetcher.fetch_top_details(detail_candidates, top_n=TOP_N_DETAILS)
        print(f"   成功抓取 {len(top_details)} 个技能详情")
        print()

        # 5. AI 总结和分类
        print(f"[步骤 5/7] AI 分析和分类...")
        summarizer = ClaudeSummarizer()
        ai_summaries = summarizer.summarize_and_classify(top_details)

        # 构建 AI 摘要映射
        ai_summary_map = {s["name"]: s for s in ai_summaries}
        print()

        # 6. 保存到数据库
        print(f"[步骤 6/7] 保存到数据库...")
        db.save_skill_details(ai_summaries)
        print()

        # 7. 计算趋势
        print(f"[步骤 7/7] 计算趋势...")
        analyzer = TrendAnalyzer(db)
        trends = analyzer.calculate_trends(today_skills, today, ai_summary_map)

        # 输出趋势摘要
        print(f"   Top 20: {len(trends['top_20'])} 个")
        print(f"   上升: {len(trends['rising_top5'])} 个")
        print(f"   下降: {len(trends['falling_top5'])} 个")
        print(f"   新晋: {len(trends['new_entries'])} 个")
        print(f"   跌出: {len(trends['dropped_entries'])} 个")
        print(f"   暴涨: {len(trends['surging'])} 个")
        print()

        # 通知输出
        reporter = HTMLReporter()

        if NOTIFY_CHANNEL == "telegram":
            print("[通知] 发送 Telegram 消息...")
            text = reporter.generate_telegram_text(trends, today)
            sender = TelegramSender(TELEGRAM_BOT_TOKEN)
            thread_id = int(TELEGRAM_MESSAGE_THREAD_ID) if TELEGRAM_MESSAGE_THREAD_ID else None
            result = sender.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=text,
                parse_mode="HTML",
                disable_web_page_preview=True,
                message_thread_id=thread_id,
            )
            if result.get("success"):
                print(f"   ✅ Telegram 发送成功! message_id: {result.get('id')}")
            else:
                print(f"   ❌ Telegram 发送失败: {result.get('message')}")
            print()

        else:  # resend
            print("[通知] 发送 Resend 邮件...")
            html_content = reporter.generate_email_html(trends, today)
            print(f"   HTML 长度: {len(html_content)} 字符")
            sender = ResendSender(RESEND_API_KEY)
            result = sender.send_email(
                to=EMAIL_TO,
                subject=f"Skills Trending Daily - {today}",
                html_content=html_content,
                from_email=RESEND_FROM_EMAIL,
            )
            if result.get("success"):
                print(f"   ✅ 邮件发送成功! ID: {result.get('id')}")
            else:
                print(f"   ❌ 邮件发送失败: {result.get('message')}")
            print()

        # 8. 清理过期数据
        print(f"[清理] 清理 {DB_RETENTION_DAYS} 天前的数据...")
        deleted = db.cleanup_old_data(DB_RETENTION_DAYS)
        print()

        # 完成
        print("╔════════════════════════════════════════════════════════════╗")
        print("║                                                              ║")
        print("║   ✅ 任务完成!                                              ║")
        print("║                                                              ║")
        print(f"║   日期: {today}                                            ║")
        print(f"║   技能数: {len(today_skills)}                                    ║")
        print(f"║   新晋: {len(trends['new_entries'])} | 跌出: {len(trends['dropped_entries'])}                         ║")
        print(f"║   暴涨: {len(trends['surging'])}                                                ║")
        print("║                                                              ║")
        print("╚════════════════════════════════════════════════════════════╝")

    except KeyboardInterrupt:
        print("\n⚠️ 用户中断")
        sys.exit(130)

    except Exception as e:
        print(f"\n[错误] 执行过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
