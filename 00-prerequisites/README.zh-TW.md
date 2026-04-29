# Chapter 00 — Prerequisites

## 本章目標

- 裝好 Claude Code、Codex CLI、Gemini CLI
- 取得三家 API key
- 估預算（目標：完成全課程 < $5）
- 用 `check-env.sh` 驗證環境

## 安裝三家 CLI

### Claude Code
官方[安裝指南](https://docs.claude.com/en/docs/claude-code)。

```bash
npm install -g @anthropic-ai/claude-code
claude --version  # 應該印出版本
```

### Codex CLI
官方[安裝指南](https://github.com/openai/codex-cli)。

```bash
npm install -g @openai/codex
codex --version
```

> **重要**：本教學需要 `codex-cli v0.125+`。較早的 `v0.121` 預設模型 `gpt-5.5`
> 已不再支援。

### Gemini CLI
官方[安裝指南](https://github.com/google-gemini/gemini-cli)。

```bash
npm install -g @google/gemini-cli
gemini --version
```

## 設 API key

```bash
# 在你的 ~/.bashrc 或 ~/.zshrc：
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export GEMINI_API_KEY="..."
```

如果你的 Codex CLI 用 ChatGPT 帳戶認證（不是 API key），看 Codex 文件的 OAuth
流程。**注意**：ChatGPT-account Codex 不能用裸 `gpt-5` 模型；要用預設的
ChatGPT-allowed model。

## macOS 使用者：裝 GNU timeout

本 repo 的腳本用 `timeout` 限制 LLM 呼叫時間。macOS 預設沒有 GNU `timeout`：

```bash
brew install coreutils    # 提供 gtimeout
```

腳本自動偵測 `timeout` 或 `gtimeout`，所以裝好後不用做別的。

## 驗證環境

```bash
bash check-env.sh
```

預期輸出：
```
✓ Found timeout: /opt/homebrew/bin/gtimeout
Checking Claude Code...
Checking Codex CLI...
Checking Gemini CLI...
✓ All checks passed.
  Add to your shell rc to skip auto-detect on every run:
    export REDTEAM_TIMEOUT_CMD=/opt/homebrew/bin/gtimeout
```

任何檢查失敗時，腳本會告訴你哪個命令失敗、要裝什麼。

## 預算估算

每次完整紅隊跑（典型 plan）：

| Plan 大小 | Token（三家合計）| 費用（USD）|
|-----------|------------------|-----------|
| 小（sample-plan.md，約 50 行）| ~5k in、~5k out | ~$0.05 |
| 中（chapter 4 BQ plan，約 100 行）| ~10k in、~12k out | ~$0.30 |
| 大（chapter 5 GCP plan，約 150 行）| ~15k in、~15k out | ~$0.50 |

整個課程（chapter 1–6 約 6 次跑）：**< $5**。

## 常見陷阱

- **macOS 沒裝 coreutils** → `timeout: command not found`。修法：
  `brew install coreutils`
- **Codex CLI v0.121 或更舊** → 「model not supported」。升到 v0.125+
- **ChatGPT 帳戶用 `gpt-5`** → 400 error。改用預設 ChatGPT-allowed model
- **Gemini CLI 在某些 region** → 第一次呼叫失敗「API not enabled」。
  在你的 GCP console 啟用對應 API
- **Windows 原生（無 WSL）** → bash `&` / `wait` 平行語法不穩定。建議用 WSL

## 下一步

[Chapter 01 — 為什麼一家 LLM 不夠](../01-why-one-llm-isnt-enough/README.zh-TW.md)
