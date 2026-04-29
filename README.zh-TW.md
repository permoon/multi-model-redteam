# multi-model-redteam

> 100 行 bash，三家 LLM 同時當你的設計紅隊。一家看不到的盲點，三家一起找。

> **不是 jailbreak 紅隊**。這是 AI 輔助軟體設計的 design review 紅隊。如果你找的是
> prompt injection / safety alignment，請看 [garak](https://github.com/leondz/garak)
> 或 [promptfoo](https://github.com/promptfoo/promptfoo)。

[English README](./README.md)

## 快速開始（5 行）

```bash
git clone https://github.com/permoon/multi-model-redteam.git
cd multi-model-redteam
export ANTHROPIC_API_KEY=... OPENAI_API_KEY=... GEMINI_API_KEY=...
bash 06-going-further/final/redteam.sh examples/sample-plan.md
# → ./redteam-out-<timestamp>/ranked.md
```

Cost：sample plan 約 $0.05；production-size plan 約 $0.50–2.00。

## 不想安裝？直接複製這個 prompt

可以貼到 Claude / ChatGPT / Gemini 任意 chat UI 直接用：[詳見英文 README 中
完整 prompt](./README.md#dont-want-to-install-copy-this-prompt-directly)

或直接打開 [`prompts/system-prompt.md`](./prompts/system-prompt.md) 複製。

## 章節索引

| # | 章節 | 學什麼 |
|---|------|--------|
| 00 | [Prerequisites](./00-prerequisites/) | 裝三家 CLI、API key、預算 |
| 01 | [為什麼一家 LLM 不夠](./01-why-one-llm-isnt-enough/) | 單家 vs 兩家的分歧 |
| 02 | [5 點失敗劇本框架](./02-the-five-frame/) | 方法論核心 |
| 03 | [平行 + 整合 + 排序](./03-parallel-and-consolidate/) | bash `&` + 第 4 次 LLM call + 嚴重度 |
| 04 | [案例：BQ pipeline](./04-case-bq-pipeline/) | 真實 BigQuery 設計，7 個漏洞 |
| 05 | [案例：GCP 部署](./05-case-gcp-deploy/) | Cloud Run + Workflows，IAM/region 陷阱 |
| 06 | [延伸方向](./06-going-further/) | 100 行 final `redteam.sh` + extension |

## 本 repo 不是什麼

- 不是 jailbreak / LLM safety 紅隊（那是另一個領域）
- 不是 polished CLI（phase 2 會是另一個 repo）
- 不是又一個 multi-agent orchestrator（這世界不需要再一個）

## 完整中文翻譯

完整中文版本將在 v1.1 推出。目前章節內文僅英文，但 prompts 與 SQL/YAML 範例語意
不依賴英文，中文圈讀者仍可使用。

## License

程式碼與文件：MIT。`prompts/` 下的三個 prompt：CC0（無須署名，自由使用）。

— Hector（[@permoon](https://github.com/permoon)）
