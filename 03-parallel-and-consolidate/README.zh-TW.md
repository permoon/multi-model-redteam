# Chapter 03 — 平行 + 整合 + 排序

一章三段 mini-lesson，三個小腳本。合起來等於
[`final/redteam.sh`](../06-going-further/final/redteam.sh) — 但每個
script 都夠小，5 分鐘讀完、可以獨立修改。

## Mini-lessons

| 段 | 腳本 | 輸入 | 輸出 | 失敗模式 |
|---|---|---|---|---|
| 3a 平行 | [`03a-parallel.sh`](./03a-parallel.sh) | `plan.md` + `system-prompt.md` | `out/{claude,codex,gemini}.md` + `out/manifest.json` | 少於 2 家成功 → abort |
| 3b 整合 | [`03b-consolidate.sh`](./03b-consolidate.sh) | 三家輸出 | `out/consolidated.md` | 缺檔自動 skip；至少要 ≥ 2 |
| 3c 排序 | [`03c-rank.sh`](./03c-rank.sh) | `consolidated.md` | `consolidated-ranked.md` | 缺輸入 → abort |

## 順序跑法

從這章資料夾下：

```bash
bash 03a-parallel.sh ../examples/sample-plan.md
bash 03b-consolidate.sh
bash 03c-rank.sh
```

三個 script 刻意解耦。你可以換掉 step 3b（consolidator）或 3c
（ranker）改用其他 model，完全不影響 parallel runner。譬如想用
Codex 來做 consolidator：

```bash
REDTEAM_CONSOLIDATOR="codex exec --skip-git-repo-check" bash 03b-consolidate.sh
```

## 你會學到什麼

### `bash &` + `wait` 達成真平行

順序跑三家約 85 秒。平行跑約 57 秒。最慢的那家決定總時間（我們的
資料裡通常是 Claude）。速度提升大概 1.5–2.4 倍，看哪家當天比較慢。
Bash 內建這個能力，根本不需要什麼 orchestration framework。

### 為什麼 bash array 跨不過 subshell

直觀的實作會試著從 background job 去更新 parent shell 的 array：

```bash
declare -A STATUS
run_team() { ...; STATUS[$name]=ok; }    # ← 在 subshell 中跑
run_team claude "..." &
wait
echo "${STATUS[claude]}"                  # ← 永遠是空的！
```

`&` 把 `run_team` 推到 subshell 裡跑。Subshell 拿到的是 parent 變數
的**副本**，更新不會回傳到 parent。Script 在 loop 裡看起來正常，
`wait` 之後神秘地回報「0 teams succeeded」。

這個 bug 在 plan v3 review 時被抓到。修法在 `03a-parallel.sh`：每
家 team 把結果寫進一個 `$name.status` 檔，parent 在 `wait` 後讀檔。
靠檔案傳 status 跨 subshell 沒問題。

### Consolidator 是第 4 次 LLM call

三家的原始 output 可能：意見不同、語意一樣但用詞不同、同一個
finding 講三種說法。`diff` 跟 `awk` 沒辦法用**語意**合併，只能用
字串。所以我們用第 4 次 LLM call 配上嚴格的 schema：

- **共識**（≥ 2 家同意）
- **獨有**（只有 1 家 — 可能是那家的 insight，也可能是另外兩家
  的盲點）
- **明顯分歧**（要 human 來解決）
- **Coverage gap**（哪些維度涵蓋稀薄）
- **Triple blind spot**（consolidator 自己加碼覺得三家都漏的；保守
  列）

詳細 instruction 在
[`../prompts/consolidation-prompt.md`](../prompts/consolidation-prompt.md)。

### 嚴重度排序不被 must-fix noise 淹沒

不管它的話，LLM 會傾向保守 — 50 行 plan 它能給你列 15 個 MUST-FIX。
Severity prompt 把 MUST-FIX 限制在 5 個以內，除非設計在架構層級就
有問題。詳見
[`../prompts/severity-prompt.md`](../prompts/severity-prompt.md)。

## 為什麼這些不直接放在 `final/redteam.sh`

[`final/redteam.sh`](../06-going-further/final/redteam.sh) 是
production 版：100 行、三步驟一檔搞定、有 manifest 跟 graceful
degradation。**那才是你實際會跑的 script**。

這三個是**教學版** — 拆開來才看得清楚。看懂這三個之後，那個 100
行的 script 你能一次讀完。

[← 回到 README](../README.zh-TW.md) · [English](./README.md)
