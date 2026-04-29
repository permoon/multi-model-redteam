# Chapter 03 — 平行 + 整合 + 排序

> 🚧 建構中 — 在 Day 3 完成。

一章三段 mini-lesson，三個腳本：

| 段 | 腳本 | 輸入 | 輸出 | 失敗模式 |
|---|---|---|---|---|
| 3a 平行 | `03a-parallel.sh` | `plan.md`、`system-prompt.md` | `out/{claude,codex,gemini}.md`、`out/manifest.json` | < 2 家成功 → abort |
| 3b 整合 | `03b-consolidate.sh` | 三家輸出 | `out/consolidated.md` | 缺檔自動 skip；至少需 ≥ 2 |
| 3c 排序 | `03c-rank.sh` | `consolidated.md` | `consolidated-ranked.md` | 缺輸入 → abort |

## 本章目標

- bash `&` + `wait` 達成真平行（vs 順序快約 3×）
- 為什麼 bash array 跨不過 subshell（改用 status file）
- 用第 4 次 LLM call 做整合（不要手 merge）
- 嚴重度排序不被 must-fix noise 淹沒

[← 回到 README](../README.zh-TW.md)
