# Chapter 06 — 延伸方向

> ### ⚠️ 先看這個 — 延伸時最常踩的三個坑
>
> 1. **成本爆炸。** 500 行 plan、三家 model、各 ~30k token = 每次
>    跑 $0.50–2.00。先用 plan 的**摘要版**（壓到 ~5k token）來迭
>    代 prompt，等方法穩定了再跑全文。沒這樣做，調 prompt 一個下
>    午就會燒掉 $20。
> 2. **共識失效（echo chamber）。** 三家都是 transformer，都從網
>    路上重疊的文字學出來，所以它們共享盲點。三家有共識**不等於**
>    真的對 — 有時只是三家一起漏了同一個東西。修法不是再加第 4
>    家，而是把「人類發現的 bug」維護成 regression 清單放進
>    consolidation prompt，讓系統從你手動抓到的 miss 持續學習。
> 3. **模型偏見會滲入 consolidation。** Claude 過度提醒、Codex 跳
>    細節、Gemini 表面化。如果 consolidation prompt 本身又跑在
>    Claude（就像 `final/redteam.sh` 預設那樣），你會在 Claude
>    的 finding 上再疊一層 Claude 的偏見。報告裡值得寫一句。但不
>    一定每次都需要解。

## 這章有什麼

- [`final/redteam.sh`](./final/redteam.sh) — 100 行（73 行非註解
  code），所有功能整合：parallel run、manifest、2-of-3 fallback、
  consolidation、severity ranking
- 本 README — 上面的三大陷阱 + 下面的延伸方向

腳本長這樣：

```bash
bash 06-going-further/final/redteam.sh examples/sample-plan.md
# → ./redteam-out-<timestamp>/
#     ├── claude.md, codex.md, gemini.md     (三家原始 output)
#     ├── manifest.json                       (status + duration)
#     ├── consolidated.md                     (consensus + unique)
#     └── ranked.md                           (severity-ranked, FINAL)
```

預設值可用環境變數蓋掉 — 見腳本最上方的註解區塊。

## 延伸方向

想再推一步的話，按工程量由小到大：

- **加第 4 家、且要不同底層架構的 model** — 譬如 Aider 接 open
  model。對 echo chamber 有幫助，但只有當底層架構真的不同才有
  用。多加一家 GPT 系列幾乎沒差。
- **接你的 PR review bot** — 拿「沒未處理的 must-fix」當 merge
  條件。注意：短 PR 的偽陽性率很高。這個方法在 design / RFC 層
  級遠比 line-level 有用。
- **多語言 plan 支援** — 目前 prompt 假設 English markdown plan。
  純 YAML、純 Terraform、純 SQL 的輸入，consolidation 那步需要
  在 prompt 裡明確提示檔案格式。
- **prompt template 模組化** — 按 domain 拆 system prompt（data
  pipeline / web service / IAM 重視 / 等等），讓 reviewer 對該
  artifact 真正重要的 failure mode 更聚焦。

## 這裡**沒有**什麼（刻意）

- `pip install` 包裝、GitHub Action、docker image、homebrew tap
- 自製 CLI flags、profile system、plugin 架構
- 漂亮的 web UI

這些都屬於未來 Phase 2 的 CLI repo，跟這個教學 repo 分開。本 repo
的重點是**方法** — 三個 prompt、一個 shell script、兩個案例。如
果你覺得方法有用、想要一個產品化版本，留意
[github.com/permoon](https://github.com/permoon) 的 Phase 2 通
知，或開個 issue 表示需求。

[← 回到 README](../README.zh-TW.md) · [English](./README.md)
