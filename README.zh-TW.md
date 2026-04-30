# multi-model-redteam

> 100 行 bash script，讓三家 LLM 一起當你的設計紅隊。一家沒看到的，另外兩家通常會接住。

> **這不是 jailbreak 紅隊**。這是 AI 輔助軟體設計的 design review 紅隊。
> 如果你找的是 prompt injection 或 safety alignment，請看
> [garak](https://github.com/leondz/garak) 或
> [promptfoo](https://github.com/promptfoo/promptfoo)。

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

貼到 Claude、ChatGPT、或 Gemini 的 chat UI 都可以，無需任何安裝。

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

> **為什麼 prompt 保持英文**：中文 prompt 跟英文 prompt 在 LLM 輸出
> 行為上會不一樣。為了方法論一致，本 repo 的 prompt 只提供英文版。
> 用英文 prompt 對中文 plan 做 review 完全可以（雙語能力夠）。

完整方法論（三家平行 + 整合 + 嚴重度排序）見下方[章節索引](#章節索引)。
單拿這個 prompt 對你常用的那家模型跑，已經會比沒這個 prompt 好；三家
平行跑出來才是真正的差距。

## 一次跑完你會得到什麼

實測範例（chapter 04 BigQuery pipeline 案例 — 完整 plan 和原始輸出
詳見 [chapter 4](./04-case-bq-pipeline/README.zh-TW.md)）：

<details>
<summary>📋 範例 finding（chapter 04，2026-04-29 canonical run，節錄）</summary>

**三家都抓到的：**

- `INSERT INTO order_events_dedup` 不具 idempotency。任何 retry 都
  會讓昨天的 row 翻倍。現有的「< 預期 50%」alert 是單向的，over-count
  完全抓不到

**只有 Claude 抓到的：**

- **Step D 的 correlated subquery 有 unqualified column references，
  所以從第二天起 imputation 那步就靜默 no-op 了。** Codex 和 Gemini
  兩家都在 review 中**引用了那段 SQL**，然後**都假設它會跑**。沒有
  人去驗證 `WHERE m2.user_id = user_id` 在 BigQuery 的 scoping rules
  下到底有沒有綁到外層 query 預期的那個 user_id。專案核心目的（補
  missing checkout 事件）會靜默失效 2-8 週才會被發現

**只有 Gemini 抓到的：**

- **Dedup 跨 partition 的午夜邊界 race。** 同一個事件在 23:59:59（Day
  1）和 00:00:02（Day 2）retry 兩次，兩筆會落到不同的日 partition。
  Step C 的 `GROUP BY` 只看當天，所以這對跨日的副本永遠不會被 dedup

**只有 Codex 抓到的：**

- **GCS CSV 被截斷、但 BQ load 仍然成功。** 最多 ~50% 的資料會靜默
  消失但仍能通過 row-count alert，因為截斷後的檔案語法仍然合法。要
  抓這個只能在 Postgres、GCS、BigQuery 三邊對 row count

完整 output：[04-case-bq-pipeline/expected-findings.md](./04-case-bq-pipeline/expected-findings.md)
（13 consensus + 11 unique + 3 triple-blind-spot finding）

</details>

## 為什麼需要這個 repo

你已經在用 Claude Code（或 Cursor、Codex CLI）幫你看設計了。它有用。
但每家都有自己的怪癖：

- **Claude** 偏向過度提醒 — 會建議一些防禦性檢查，其實並不是 bug
- **Codex** 較簡短直接，偶爾會跳過整合層的細節
- **Gemini** 停在表面，不一定會深入特定問題

讓三家對同一份 plan、用同一份 prompt、彼此看不到對方的輸出。然後
把三家的 finding 整合起來。**只有一家抓到的問題，價值最高** — 那是
另外兩家會漏的、單家 review 永遠看不到的東西。

## 你會做出什麼

七章看完，你會有：

- 一個 100 行的 `redteam.sh`，吃任何 `plan.md`，吐出三家平行跑出來
  的 severity-ranked finding 報告
- 5 點失敗維度框架的可重用 prompt
- 兩個從頭做完的真實案例：一個 BigQuery pipeline、一個 GCP Cloud
  Run 部署

## Prerequisites

- **Bash 4+**（Windows 用 Git Bash、macOS 預設 bash 3.2 也 OK）
- **GNU `timeout`**（macOS 使用者：`brew install coreutils` 會給你
  `gtimeout`，腳本會自動偵測）
- 三家 LLM CLI 都裝好且認證過：
  - [Claude Code](https://docs.claude.com/en/docs/claude-code)
  - [Codex CLI](https://github.com/openai/codex-cli)
  - [Gemini CLI](https://github.com/google-gemini/gemini-cli)
- 三家的 API key（chapter 1-3 用 free tier 即可；chapter 4-5 約需
  $5 總計）

> **測試版本**：claude-code v2.1.114、codex-cli v0.125.0、gemini-cli v0.36.0
> （as of 2026-04）。三家 CLI **不是 stable public API**，flags、auth、
> default model 隨時可能變。如果你的版本不同，見
> [00-prerequisites](./00-prerequisites/README.zh-TW.md)。

完整安裝見 [00-prerequisites](./00-prerequisites/README.zh-TW.md)。

## 章節索引

| # | 章節 | 學什麼 |
|---|------|--------|
| 00 | [Prerequisites](./00-prerequisites/README.zh-TW.md) | 裝三家 CLI、API key、預算 |
| 01 | [為什麼一家 LLM 不夠](./01-why-one-llm-isnt-enough/README.zh-TW.md) | 一家 vs 兩家的分歧 |
| 02 | [5 點失敗劇本框架](./02-the-five-frame/README.zh-TW.md) | 方法論核心 |
| 03 | [平行 + 整合 + 排序](./03-parallel-and-consolidate/README.zh-TW.md) | bash `&` + 第 4 次 LLM call + 嚴重度 |
| 04 | [案例：BQ pipeline](./04-case-bq-pipeline/README.zh-TW.md) | 真實 BigQuery 設計，7 個藏起來的漏洞 |
| 05 | [案例：GCP 部署](./05-case-gcp-deploy/README.zh-TW.md) | Cloud Run + Workflows，IAM 和 region 陷阱 |
| 06 | [延伸方向](./06-going-further/README.zh-TW.md) | 100 行 final `redteam.sh` + extension |

## 本 repo 不是什麼

- **不是 jailbreak / safety-alignment 紅隊。** 那是另一個領域。
  請看 [garak](https://github.com/leondz/garak) 或
  [promptfoo](https://github.com/promptfoo/promptfoo)
- **不是 polished CLI。** Phase 2 會是另一個 repo，會有 `pip install`、
  GitHub Actions 之類的東西。這個 repo 是教學
- **不是又一個 multi-agent orchestrator。** 那種已經夠多了

## Standalone prompts

[`prompts/`](./prompts/README.zh-TW.md) 裡的三個 prompt 採 **CC0**。
chat UI、自己的 pipeline、內部工具，要拿去哪裡用都可以。歡迎署名但不必要。

## License

程式碼和文件：MIT。`prompts/` 下的 prompt：CC0。

## Acknowledgements

主要靈感來自：
- [karpathy/micrograd](https://github.com/karpathy/micrograd) — 短小精悍的教學
  repo 應該長什麼樣
- [rasbt/LLMs-from-scratch](https://github.com/rasbt/LLMs-from-scratch) —
  章節資料夾的版型

— Hector（[@permoon](https://github.com/permoon)）
