# multi-model-redteam

> 100 行 bash，三家 LLM 同時當你的設計紅隊。一家看不到的盲點，三家一起找。

> **不是 jailbreak 紅隊**。這是 AI 輔助軟體設計的 design review 紅隊。如果你找的是
> prompt injection / safety alignment，請看 [garak](https://github.com/leondz/garak)
> 或 [promptfoo](https://github.com/promptfoo/promptfoo)。

[English README](./README.md) · [方法論](./docs/methodology.zh-TW.md) · [章節索引](#章節索引)

![demo](./assets/hero.gif)

## 快速開始（5 行）

```bash
git clone https://github.com/permoon/multi-model-redteam.git
cd multi-model-redteam
export ANTHROPIC_API_KEY=... OPENAI_API_KEY=... GEMINI_API_KEY=...
bash 06-going-further/final/redteam.sh examples/sample-plan.md
# → ./redteam-out-<timestamp>/ranked.md
```

費用：sample plan 約 $0.05；production-size plan 約 $0.50–2.00。

## 不想安裝？直接複製這個 prompt

可以貼到 Claude / ChatGPT / Gemini 任意 chat UI，無需任何安裝：

<details>
<summary>📋 5 點失敗維度紅隊 prompt（保持英文，這是設計選擇）</summary>

```
You are the red team for this design.

Cover all 5 dimensions below. For each, provide AT LEAST 2 concrete failure
scenarios (not abstract descriptions):

1. HIDDEN ASSUMPTIONS — ordering, uniqueness, atomicity, data freshness,
   caller behavior. What does this design implicitly depend on?
2. DEPENDENCY FAILURES — upstream/downstream services, external APIs,
   databases, messaging. What breaks if any dependency degrades?
3. BOUNDARY INPUTS — empty, single, huge batch, malicious, malformed.
   What happens at p99 and at malicious-percentile inputs?
4. MISUSE PATHS — caller misbehavior, user skipping steps, out-of-order
   operations. What if humans don't follow the plan?
5. ROLLBACK & BLAST RADIUS — how to recover, scope of damage. 5-minute
   detection vs 5-day detection?

For each scenario, include:
- TRIGGER: what causes it
- IMPACT: who is affected, how badly
- DETECTABILITY: how long until noticed

Be concrete. Reject abstract advice like "add monitoring". Specify what
metric, what threshold, what alert.

Design to review:
---
{PASTE PLAN HERE}
---
```

</details>

> **為什麼 prompt 保持英文**：中文 prompt 與英文 prompt 在 LLM 輸出行為上會不同。
> 為了方法論一致性，本 repo 的 prompt 只提供英文版。LLM 對中文 plan 用英文
> prompt review 完全可行（雙語能力夠）。

完整方法論（三家平行 + 整合 + 嚴重度排序）見下方[章節索引](#章節索引)。

## 一次跑完你會得到什麼

實測範例（chapter 04 BigQuery pipeline 案例 — 詳見
[chapter 4](./04-case-bq-pipeline/README.zh-TW.md)）：

<details>
<summary>📋 範例 finding（chapter 04，2026-04-29 canonical run，節錄）</summary>

**Consensus（三家都抓到）：**

- `INSERT INTO order_events_dedup` 不具 idempotency。任何 retry 都會
  讓昨天的 row 翻倍。現有「< 預期 50%」的 alert 是單向的，抓不到
  over-count

**Claude 獨家：**

- **Step D 的 correlated subquery 有 unqualified column references →
  imputation 從第二天起靜默 no-op。** Codex 和 Gemini 兩家**都引用了
  同一段 SQL** 並分析下游行為，但**都假設它能跑**。沒人去檢查
  `WHERE m2.user_id = user_id` 在 BigQuery 的 scoping rules 下是否
  真的綁到外層 query。專案的核心目標（補 missing checkout 事件）
  會靜默失效 2-8 週，沒人會注意

**Gemini 獨家：**

- **Dedup 跨 partition 的午夜邊界 race。** 同一個事件在 23:59:59（Day
  1）和 00:00:02（Day 2）retry 兩次，會落到不同的日 partition。
  Step C 的 `GROUP BY` 只看當天，這對跨分區的副本永遠不會被 dedup

**Codex 獨家：**

- **GCS CSV 被截斷、BQ load 仍然成功。** 最多 ~50% 的靜默資料遺失
  可以通過 row-count alert，因為截斷後的檔案仍然語法合法。需要
  Postgres ↔ GCS ↔ BQ 三方 row count 對帳才能偵測

完整 output：[04-case-bq-pipeline/expected-findings.md](./04-case-bq-pipeline/expected-findings.md)
（13 consensus + 11 unique + 3 triple-blind-spot finding）

</details>

## 為什麼需要這個 repo

你已經會用 Claude Code（或 Cursor、Codex CLI）review 設計。它能抓到很多東西。
但每個 model 都有盲點：

- **Claude** 過度防禦性
- **Codex** 跳過整合細節
- **Gemini** 停在表面

讓**三家**對同一份 plan 平行跑、用同一份 prompt、彼此看不到輸出。然後整合。
**只有一家抓到的 finding 才是金礦**。

## 你會做出什麼

完成 7 章後：
- 一個 `redteam.sh`（< 100 行），吃任何 `plan.md`，產出嚴重度排序的 finding 報告
- 5 點失敗維度框架的可重用 prompt
- 兩個真實案例：BigQuery pipeline + GCP Cloud Run 部署

## Prerequisites

- **Bash 4+**（Windows 用 Git Bash、macOS 預設 bash 3.2 也 OK）
- **GNU `timeout`**（macOS 使用者：`brew install coreutils` 會給你 `gtimeout`，
  腳本會自動偵測）
- 三家 LLM CLI 都裝好且已認證：
  - [Claude Code](https://docs.claude.com/en/docs/claude-code)
  - [Codex CLI](https://github.com/openai/codex-cli)
  - [Gemini CLI](https://github.com/google-gemini/gemini-cli)
- 三家的 API key（chapter 1–3 用 free tier 即可；chapter 4–5 約需 $5 總計）

> **測試版本**：claude-code v2.1.114、codex-cli v0.125.0、gemini-cli v0.36.0
> （as of 2026-04）。三家 CLI **不是 stable public API**，flags / auth /
> default model 隨時可能變。如果你的版本不同，見
> [00-prerequisites](./00-prerequisites/README.zh-TW.md)。

詳細安裝見 [00-prerequisites](./00-prerequisites/README.zh-TW.md)。

## 章節索引

| # | 章節 | 學什麼 |
|---|------|--------|
| 00 | [Prerequisites](./00-prerequisites/README.zh-TW.md) | 裝三家 CLI、API key、預算 |
| 01 | [為什麼一家 LLM 不夠](./01-why-one-llm-isnt-enough/README.zh-TW.md) | 單家 vs 兩家的分歧 |
| 02 | [5 點失敗劇本框架](./02-the-five-frame/README.zh-TW.md) | 方法論核心 |
| 03 | [平行 + 整合 + 排序](./03-parallel-and-consolidate/README.zh-TW.md) | bash `&` + 第 4 次 LLM call + 嚴重度 |
| 04 | [案例：BQ pipeline](./04-case-bq-pipeline/README.zh-TW.md) | 真實 BigQuery 設計，7 個漏洞 |
| 05 | [案例：GCP 部署](./05-case-gcp-deploy/README.zh-TW.md) | Cloud Run + Workflows，IAM/region 陷阱 |
| 06 | [延伸方向](./06-going-further/README.zh-TW.md) | 100 行 final `redteam.sh` + extension |

## 本 repo 不是什麼

- **不是 jailbreak / safety-alignment 紅隊**。那是另一個領域。
- **不是 polished CLI**。Phase 2 會是另一個 repo（`pip install`、GitHub Actions、
  docker image 等）。本 repo 是教學。
- **不是又一個 multi-agent orchestrator**。這世界不需要再一個。

## Standalone prompts

[`prompts/`](./prompts/README.zh-TW.md) 中的三個 prompt 採用 **CC0** 授權。
chat UI、自家 pipeline、內部工具，任何地方自由使用。歡迎署名但不必要。

## License

程式碼與文件：MIT。`prompts/` 下的 prompt：CC0。

## Acknowledgements

主要靈感來自：
- [karpathy/micrograd](https://github.com/karpathy/micrograd) — 短小精悍教學的標竿
- [rasbt/LLMs-from-scratch](https://github.com/rasbt/LLMs-from-scratch) —
  章節資料夾型版型

— Hector（[@permoon](https://github.com/permoon)）
