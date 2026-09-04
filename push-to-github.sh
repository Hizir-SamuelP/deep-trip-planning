#!/usr/bin/env bash
# 推送 deep-trip-planning 到 GitHub
#
# 用法：在本目录（github-deep-trip-planning/）打开终端，运行
#     bash push-to-github.sh
#
# 仓库 https://github.com/Hizir-SamuelP/deep-trip-planning 已存在。
# 如果它里面已经有 README 之类的文件，push 会被拒绝——那种情况看脚本末尾的提示。

set -e

USER="${1:-Hizir-SamuelP}"
REPO="deep-trip-planning"

if [ -d .git ]; then
  echo "⚠️  当前目录已经有 .git 了。如果是上次跑到一半，先删掉再重来："
  echo "    rm -rf .git && bash push-to-github.sh"
  exit 1
fi

git init -b main
git add -A
git commit -m "deep-trip-planning: a Claude Skill for itineraries you can actually follow

Extracted and generalized from a real 8-day trip that went through the full
cycle: planning, per-store verification, budget, hotel comparison, and a
mid-planning airport change.

- SKILL.md: 8-step workflow, preferences-as-dials, decision thresholds
- references/: verification, transit & maps, lodging decisions, budget & customs
- evals/: 3 test prompts used to benchmark against a no-skill baseline (25/25 vs 19/25)"

git remote add origin "https://github.com/$USER/$REPO.git"

echo
echo "→ 正在推送。如果弹出登录，用 GitHub 用户名 + Personal Access Token（不是密码）。"
echo

if git push -u origin main; then
  echo
  echo "✅ 完成：https://github.com/$USER/$REPO"
  echo
  echo "建议再做两件事："
  echo "  1. 仓库页面右上角齿轮 → Topics 加上："
  echo "     claude-skill  agent-skills  travel-planning  itinerary  ai-agent"
  echo "  2. About 里填一句描述，比如："
  echo "     A Claude Skill that turns a list of places into an itinerary you can actually follow."
else
  echo
  echo "❌ push 被拒绝了。最常见的原因是仓库里已经有文件（比如建仓库时勾了 README）。"
  echo "   解决办法二选一："
  echo "     A) 保留远端内容并合并："
  echo "        git pull --rebase origin main && git push -u origin main"
  echo "     B) 远端是空的/不要了，直接覆盖："
  echo "        git push -u --force origin main"
  exit 1
fi
