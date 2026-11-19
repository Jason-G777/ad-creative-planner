#!/usr/bin/env python3
"""
轻量广告文案与提案去 AI 味自检脚本（零第三方依赖）
用法：
  python3 scripts/check_copy.py <文案或Markdown文件路径>
  echo "你的文案内容" | python3 scripts/check_copy.py
"""

import re
import sys
from pathlib import Path

BANNED_BUZZWORDS = [
    "赋能",
    "重塑",
    "升维",
    "破局",
    "闭环",
    "穿透",
    "引领",
    "致敬",
    "匠心",
    "全域引爆",
    "价值跃升",
    "深度共振",
    "构建生态",
]

AI_PATTERNS = [
    (r"不仅是.{1,25}更是", "高频 AI 句模：不仅是……更是……"),
    (r"不只是.{1,25}更是", "高频 AI 句模：不只是……更是……"),
    (r"从.{1,20}切入.{0,6}自然带出", "高频 AI 句模：从……切入，自然带出……"),
    (r"被看见.{0,4}被理解.{0,4}被记住", "高频 AI 句模：被看见、被理解、被记住"),
    (r"以.{1,15}为抓手", "公文/AI 黑话句模：以……为抓手"),
    (r"在.{1,20}的浪潮下", "空洞开场句模：在……的浪潮下"),
]

DIRECTORY_TITLES = [
    "市场分析",
    "背景分析",
    "消费者洞察",
    "人群洞察",
    "传播规划",
    "营销策略",
    "总结",
]


def inspect_text(text: str) -> list[str]:
    findings: list[str] = []
    lines = text.splitlines()

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            continue

        for word in BANNED_BUZZWORDS:
            if word in stripped:
                findings.append(f"[第 {idx} 行][禁用黑话] 命中「{word}」→ {stripped[:60]}")

        for pattern, label in AI_PATTERNS:
            if re.search(pattern, stripped):
                findings.append(f"[第 {idx} 行][AI 句模] {label} → {stripped[:60]}")

        if stripped.startswith("#"):
            title_body = stripped.lstrip("#").strip()
            for dir_title in DIRECTORY_TITLES:
                if title_body == dir_title:
                    findings.append(
                        f"[第 {idx} 行][标题即结论提醒] 标题「{title_body}」偏目录腔，建议改为有判断的结论句"
                    )
            if len(title_body) > 32:
                findings.append(
                    f"[第 {idx} 行][标题偏长] 当前 {len(title_body)} 字（建议 PPT 标题控制在 15–28 字内）→ {title_body[:40]}..."
                )

    return findings


def main() -> int:
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
        if not file_path.exists():
            print(f"错误：找不到文件 {file_path}", file=sys.stderr)
            return 2
        text = file_path.read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()

    findings = inspect_text(text)
    if not findings:
        print("PASS：未检测到禁用黑话、高频 AI 句模或明显目录腔标题。")
        return 0

    print(f"发现 {len(findings)} 处可优化项：")
    for item in findings:
        print(f"- {item}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
