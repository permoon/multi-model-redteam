# Chapter 00 — Prerequisites

Chapter 1 開始前要先裝幾個東西。如果這幾個 CLI 你都沒用過，大概 10
分鐘可以裝完；用過的話更快。

## 這章你會做什麼

- 裝好 Claude Code、Codex CLI、Gemini CLI
- 取得三家的 API key
- 估一下預算（目標：完成整個課程花不到 $5）
- 跑 `check-env.sh` 確認一切都對

## 裝三家 CLI

### Claude Code

[官方安裝指南](https://docs.claude.com/en/docs/claude-code)。

```bash
npm install -g @anthropic-ai/claude-code
claude --version  # 應該印出版本
```

### Codex CLI

[官方安裝指南](https://github.com/openai/codex-cli)。

```bash
npm install -g @openai/codex
codex --version
```

> **重要**：本教學需要 `codex-cli v0.125+`。較早的 `v0.121` 預設模型
> 是 `gpt-5.5`，已經不支援。如果你的版本舊請升級。

### Gemini CLI

[官方安裝指南](https://github.com/google-gemini/gemini-cli)。

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

如果你的 Codex CLI 用 ChatGPT 帳號認證（不是 API key），看 Codex 文
件的 OAuth 流程。**注意**：ChatGPT-account Codex 不能用裸 `gpt-5`
模型，請用預設的 ChatGPT-allowed model。

## macOS 使用者：裝 GNU timeout

這個 repo 的腳本用 `timeout` 限制 LLM 呼叫時間。macOS 預設沒裝
GNU `timeout`：

```bash
brew install coreutils    # 提供 gtimeout
```

腳本會自動偵測 `timeout` 或 `gtimeout`，所以裝好就好，不用做別的事。

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

任何檢查失敗時，腳本會告訴你哪個命令、要裝什麼。

## 預算

每次完整紅隊跑，依 plan 大小：

| Plan 大小 | Token（三家合計）| 費用（USD）|
|-----------|------------------|-----------|
| 小（sample-plan.md，約 50 行）| ~5k in、~5k out | ~$0.05 |
| 中（chapter 4 BQ plan，約 100 行）| ~10k in、~12k out | ~$0.30 |
| 大（chapter 5 GCP plan，約 150 行）| ~15k in、~15k out | ~$0.50 |

整個課程（chapter 1–6 約 6 次跑）：**$5 以內**。

## 常見會踩到的坑

實際讀者撞過的問題：

- **macOS 沒裝 coreutils。** 錯誤：`timeout: command not found`。
  修法：`brew install coreutils`。
- **Codex CLI v0.121 或更舊。** 錯誤訊息會提到「model not
  supported」。修法：升到 v0.125+。
- **ChatGPT 帳號用 `gpt-5`。** 回 400。改用預設的 ChatGPT-allowed
  model。
- **Gemini CLI 在某些 region。** 第一次呼叫失敗「API not enabled」。
  到你的 GCP console 啟用對應 API。
- **Windows 原生（沒 WSL）。** Bash `&` 和 `wait` 平行語法在那裡
  不太穩。建議用 WSL。

## 下一步

[Chapter 01 — 為什麼一家 LLM 不夠](../01-why-one-llm-isnt-enough/README.zh-TW.md)

[← 回到 README](../README.zh-TW.md) · [English](./README.md)
