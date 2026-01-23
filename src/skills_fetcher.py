"""
Skills Fetcher - 从 skills.sh/trending 获取技能排行榜
"""
import re
import json
import time
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import requests

from src.config import SKILLS_TRENDING_URL, SKILLS_BASE_URL


class SkillsFetcher:
    """从 skills.sh/trending 获取排行榜"""

    def __init__(self, timeout: int = 30):
        """
        初始化

        Args:
            timeout: 请求超时时间（秒）
        """
        self.base_url = SKILLS_BASE_URL
        self.trending_url = SKILLS_TRENDING_URL
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; SkillsTrendingBot/1.0)"
        })

    def fetch(self) -> List[Dict]:
        """
        获取 Top 100 技能列表

        Returns:
            [
                {
                    "rank": 1,
                    "name": "remotion-best-practices",
                    "owner": "remotion-dev/skills",
                    "installs": 5600,
                    "url": "https://skills.sh/remotion-dev/skills/remotion-best-practices"
                },
                ...
            ]
        """
        print(f"📡 正在获取榜单: {self.trending_url}")

        try:
            # 方式1: 尝试从页面中提取内联 JSON 数据
            html_content = self.fetch_trending_page()
            skills = self.parse_from_json(html_content)

            if skills:
                print(f"✅ 从 JSON 提取到 {len(skills)} 个技能")
                return skills

            # 方式2: 如果 JSON 解析失败，尝试解析 HTML
            print("⚠️ JSON 解析失败，尝试解析 HTML...")
            skills = self.parse_from_html(html_content)

            if skills:
                print(f"✅ 从 HTML 提取到 {len(skills)} 个技能")
                return skills

            raise Exception("无法从页面解析技能列表")

        except Exception as e:
            print(f"❌ 获取榜单失败: {e}")
            raise

    def fetch_trending_page(self) -> str:
        """
        获取 trending 页面 HTML

        Returns:
            页面 HTML 内容
        """
        try:
            response = self.session.get(self.trending_url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise Exception(f"请求 trending 页面失败: {e}")

    def parse_from_json(self, html_content: str) -> Optional[List[Dict]]:
        """
        从页面中提取内联 JSON 数据

        Args:
            html_content: 页面 HTML

        Returns:
            技能列表，如果解析失败返回 None
        """
        # 尝试查找 Next.js 的数据
        # 通常在 <script id="__NEXT_DATA__" type="application/json"> 中
        pattern = r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>'
        match = re.search(pattern, html_content, re.DOTALL)

        if not match:
            # 尝试其他可能的 JSON 格式
            pattern = r'<script[^>]*type="application/json"[^>]*>(.*?)</script>'
            match = re.search(pattern, html_content, re.DOTALL)

        if not match:
            return None

        try:
            json_str = match.group(1)
            data = json.loads(json_str)

            # 尝试从不同的路径提取数据
            skills = self._extract_skills_from_nextjs_data(data)

            return skills

        except json.JSONDecodeError:
            return None

    def _extract_skills_from_nextjs_data(self, data: dict) -> Optional[List[Dict]]:
        """
        从 Next.js 数据结构中提取技能列表

        Args:
            data: 解析后的 JSON 数据

        Returns:
            技能列表
        """
        # 尝试不同的路径
        paths = [
            ["props", "pageProps", "skills"],
            ["props", "pageProps", "leaderboard"],
            ["props", "pageProps", "initialState", "skills"],
            ["props", "initialProps", "pageProps", "skills"],
        ]

        for path in paths:
            current = data
            try:
                for key in path:
                    current = current[key]
                if isinstance(current, list):
                    return self._normalize_skills_data(current)
            except (KeyError, TypeError):
                continue

        return None

    def _normalize_skills_data(self, raw_skills: List) -> List[Dict]:
        """
        标准化技能数据

        Args:
            raw_skills: 原始技能数据

        Returns:
            标准化后的技能列表
        """
        skills = []

        for item in raw_skills:
            if not isinstance(item, dict):
                continue

            # 处理不同的数据格式
            skill = {
                "rank": self._extract_rank(item),
                "name": self._extract_name(item),
                "owner": self._extract_owner(item),
                "installs": self._extract_installs(item),
                "url": self._extract_url(item)
            }

            if skill["name"] and skill["rank"]:
                skills.append(skill)

        return skills

    def _extract_rank(self, item: dict) -> Optional[int]:
        """提取排名"""
        for key in ["rank", "position", "number", "#"]:
            if key in item:
                value = item[key]
                try:
                    return int(value)
                except (ValueError, TypeError):
                    continue
        return None

    def _extract_name(self, item: dict) -> Optional[str]:
        """提取技能名称"""
        for key in ["name", "skill", "slug", "title"]:
            if key in item and item[key]:
                return str(item[key]).strip()
        return None

    def _extract_owner(self, item: dict) -> str:
        """提取拥有者"""
        for key in ["owner", "author", "repository", "repo"]:
            if key in item and item[key]:
                return str(item[key])
        return "unknown"

    def _extract_installs(self, item: dict) -> int:
        """提取安装量"""
        for key in ["installs", "installCount", "downloads", "count"]:
            if key in item:
                value = item[key]
                try:
                    # 处理 "5.6K" 这样的格式
                    if isinstance(value, str):
                        value = value.upper()
                        if "K" in value:
                            return int(float(value.replace("K", "")) * 1000)
                        return int(value)
                    return int(value)
                except (ValueError, TypeError):
                    continue
        return 0

    def _extract_url(self, item: dict) -> str:
        """提取技能 URL"""
        if "url" in item and item["url"]:
            return item["url"]

        # 如果没有 URL，尝试构建
        name = self._extract_name(item)
        owner = self._extract_owner(item)

        if name and owner:
            return f"{self.base_url}/{owner}/{name}"

        return ""

    def parse_from_html(self, html_content: str) -> List[Dict]:
        """
        从 HTML 解析技能列表（备用方案）

        Args:
            html_content: 页面 HTML

        Returns:
            技能列表
        """
        soup = BeautifulSoup(html_content, "lxml")
        skills = []

        # 尝试找到排行榜的容器
        # 根据实际页面结构调整选择器
        leaderboard_selectors = [
            "table",
            '[class*="leaderboard"]',
            '[class*="ranking"]',
            '[class*="skills"]',
            "ol",
            "ul"
        ]

        for selector in leaderboard_selectors:
            container = soup.select_one(selector)
            if container:
                skills = self._parse_leaderboard_container(container)
                if skills:
                    break

        return skills

    def _parse_leaderboard_container(self, container) -> List[Dict]:
        """
        解析排行榜容器

        Args:
            container: BeautifulSoup 元素

        Returns:
            技能列表
        """
        skills = []
        rank = 1

        # 尝试不同的列表项选择器
        item_selectors = ["li", "tr", '[class*="item"]', '[class*="row"]']

        for item_selector in item_selectors:
            items = container.select(item_selector)

            if len(items) > 5:  # 至少有 5 项才认为找到正确容器
                for item in items:
                    skill = self._parse_skill_item(item, rank)
                    if skill:
                        skills.append(skill)
                        rank += 1
                break

        return skills

    def _parse_skill_item(self, item, rank: int) -> Optional[Dict]:
        """
        解析单个技能项

        Args:
            item: BeautifulSoup 元素
            rank: 排名

        Returns:
            技能字典或 None
        """
        try:
            # 查找链接
            link = item.find("a", href=True)
            if not link:
                return None

            href = link.get("href", "")

            # 解析技能名称和拥有者
            # URL 格式: /owner/repo 或 /owner/skills/skill-name
            parts = href.strip("/").split("/")

            if len(parts) >= 2:
                if parts[-2] == "skills":
                    # /owner/skills/skill-name
                    owner = f"{parts[-3]}/skills"
                    name = parts[-1]
                else:
                    # /owner/repo
                    owner = parts[-2]
                    name = parts[-1]

                # 提取安装量
                installs_text = item.get_text()
                installs_match = re.search(r'(\d+(?:\.\d+)?K?)', installs_text)
                installs = 0
                if installs_match:
                    installs_str = installs_match.group(1).upper()
                    if "K" in installs_str:
                        installs = int(float(installs_str.replace("K", "")) * 1000)
                    else:
                        installs = int(installs_str)

                return {
                    "rank": rank,
                    "name": name,
                    "owner": owner,
                    "installs": installs,
                    "url": f"{self.base_url}{href}"
                }
        except Exception as e:
            pass

        return None

    def get_date_range(self) -> tuple:
        """
        获取可用日期范围

        Returns:
            (earliest_date, latest_date) 或 (None, None)
        """
        # 这个方法需要数据库支持，由 Database 类提供
        return None, None


def fetch_skills() -> List[Dict]:
    """便捷函数：获取技能列表"""
    fetcher = SkillsFetcher()
    return fetcher.fetch()
