# Chapter 03 — 平行 + 整合 + 排序

一章三段 mini-lesson，三個腳本。合起來重現
[`final/redteam.sh`](../06-going-further/final/redteam.sh) — 但每個 script
夠小，5 分鐘讀完，可獨立修改。

## Mini-lessons

| 段 | 腳本 | 輸入 | 輸出 | 失敗模式 |
|---|---|---|---|---|
| 3a 平行 | [`03a-parallel.sh`](./03a-parallel.sh) | `plan.md` + `system-prompt.md` | `out/{claude,codex,gemini}.md` + `out/manifest.json` | < 2 家成功 → abort |
| 3b 整合 | [`03b-consolidate.sh`](./03b-consolidate.sh) | 三家輸出 | `out/consolidated.md` | 缺檔自動 skip；至少需 ≥ 2 |
| 3c 排序 | [`03c-rank.sh`](./03c-rank.sh) | `consolidated.md` | `consolidated-ranked.md` | 缺輸入 → abort |

## 順序跑法

從本章節資料夾下：

```bash
bash 03a-parallel.sh ../examples/sample-plan.md
bash 03b-consolidate.sh
bash 03c-rank.sh
```

三個 script 刻意解耦 — 你可以換 step 3b（consolidator）或 3c（ranker）為其他
model，不影響 parallel runner。譬如用 Codex 做 consolidator：

```bash
REDTEAM_CONSOLIDATOR="codex exec --skip-git-repo-check" bash 03b-consolidate.sh
```

## 你會學到

### `bash &` + `wait` 達成真平行

順序跑三家約 85 秒。平行跑約 57 秒（最慢的一家決定總時間，我們的數據是 Claude）。
速度提升約 1.5–2.4 倍（看哪家當天慢）。Bash 內建這個能力，不需要 orchestration
framework。

### 為什麼 bash array 跨不過 subshell

直觀的實作會試著從 background job 更新 parent shell array：

```bash
declare -A STATUS
run_team() { ...; STATUS[$name]=ok; }    # ← 在 subshell 中跑
run_team claude "..." &
wait
echo "${STATUS[claude]}"                  # ← 永遠是空的！
```

`&` 把 `run_team` 放進 subshell。Subshell 拿到 parent 變數的**副本**。更新
不會回傳。Script 在 loop 中看似 OK，wait 後神秘地報「0 teams succeeded」。

這個 bug 在 plan v3 review 時被抓到。修法在 `03a-parallel.sh`：每家 team 寫
一個 `$name.status` 檔，parent 在 wait 後讀檔。檔案 status 跨 subshell 邊界
乾淨無誤。

### Consolidator 用第 4 次 LLM call

三家 raw output 可能：意見不同、語意相同但用詞不同、同一 finding 三種說法。
`diff` 跟 `awk` 不能用**語意**合併，只能用字串。所以我們用第 4 次 LLM call
配嚴格 schema：

- **共識**（≥ 2 家）
- **獨有**（1 家 — 可能是 insight 或別家盲點）
- **明顯分歧**（要 human 解決）
- **Coverage gap**（哪些維度涵蓋稀薄）
- **Triple blind spot**（consolidator 自己加碼指出，保守）

詳細 instruction 見 [`../prompts/consolidation-prompt.md`](../prompts/consolidation-prompt.md)。

### 嚴重度排序不被 must-fix noise 淹沒

LLM 傾向保守 — 放任不管，50 行 plan 它會給 15 個 MUST-FIX。Severity prompt
限制 MUST-FIX ≤ 5（除非設計在架構層級壞掉）。詳見
[`../prompts/severity-prompt.md`](../prompts/severity-prompt.md)。

## 為什麼這些不放在 `final/redteam.sh`

[`final/redteam.sh`](../06-going-further/final/redteam.sh) 是 production 版：
100 行、三步驟同檔、含 manifest + graceful degradation。**那才是你實際跑的 script**。

這三個是**教學版** — 拆開為了清楚。看懂這三個後，你能一次讀完
`final/redteam.sh`。

[← 回到 README](../README.zh-TW.md) · [English](./README.md)
