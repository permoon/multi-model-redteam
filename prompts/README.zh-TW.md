# Prompts

本教學的核心 IP — 三個 prompt。**採用 CC0 授權** — 自由複製，無需署名。

| 檔案 | 用途 |
|------|------|
| [`system-prompt.md`](./system-prompt.md) | 5 點失敗維度紅隊 prompt。可對任何設計 plan 使用 |
| [`consolidation-prompt.md`](./consolidation-prompt.md) | 把三份獨立 review 整合成共識 + 獨有 finding |
| [`severity-prompt.md`](./severity-prompt.md) | 把 finding 排為 must-fix / should-fix / accept |

## Standalone 使用（無需安裝）

不需要整個 repo。把 `system-prompt.md` + 你的 plan 貼進任何 LLM chat UI：

- [Claude](https://claude.ai) 或 Claude Code
- [ChatGPT](https://chat.openai.com) 或 Codex CLI
- [Gemini](https://gemini.google.com) 或 Gemini CLI

完整 multi-LLM workflow（三家平行 + 整合 + 排序），見
[課程章節](../README.zh-TW.md#章節索引)。

## 為什麼用 CC0

這些 prompt 是本 repo 的方法論核心。CC0 授權代表：
- 採用無摩擦 — 任何人可在商業專案中使用
- 無署名負擔 — 直接複製進你內部工具
- 無授權衝突 — 跟任何下游 license 兼容

repo 其他部分的程式碼採 MIT。

## 為什麼 prompt 內容只提供英文

中文 prompt 與英文 prompt 在 LLM 輸出行為上會有差異。為了方法論一致性，
本 repo 的三個 prompt 只維護英文版。對中文 plan 用英文 prompt review 完全可行
（LLM 雙語能力夠）。如果你要用中文 prompt，請自己 fork 一份。

## 變體

要 fork 這些 prompt 給你團隊的領域用？常見改法：
- 加第 6 個維度（如「合規」對受監管產業）
- 把 `MUST-FIX / SHOULD-FIX / ACCEPT` 改成你團隊的嚴重度標準
- 收緊 / 放寬「每維度 ≥2 個具體劇本」規則

如果你做了有用的變體，歡迎開 issue / PR 分享 use case（不必要）。
