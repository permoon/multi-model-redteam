# Chapter 01 — 為什麼一家 LLM 不夠

你已經在用 Claude Code（或 Cursor、Codex CLI）幫你看 code 了。它確實
有用，會抓到不少問題。那為什麼還要再多塞一家進來？甚至再多兩家？

與其問，不如直接試。下面準備了 28 行 Python，藏了 5 個 bug。你會跑
一個小腳本，讓 Claude 跟 Codex 各看一次，把兩份意見並排放著。一分鐘
跑完，花你 $0.02。看完你就會懂為什麼一家不夠。

## 檔案

- [`target-code.py`](./target-code.py) — 28 行 Python，藏了 5 個 bug。
  Bug 清單只放在本 README，不放在 code 註解裡，避免模型偷看到答案。
- [`compare-models.sh`](./compare-models.sh) — 先跑 Claude、再跑 Codex，
  兩份意見分別存到 `review-claude.md` / `review-codex.md`

## 怎麼跑

```bash
cd 01-why-one-llm-isnt-enough
bash compare-models.sh
# → review-claude.md
# → review-codex.md
```

費用：約 $0.02。對 28 行 code 跑兩次而已。

## Code 在做什麼

是一段「訂單計分批次」 — 每筆 event 進來，先用 user 去重複，再寫一
筆計分到 SQLite，最後把累計的 loyalty 點數推給下游 API。看起來
還好。但有 5 個問題。

1. **去重複只看 `user_id`。** 同一個人下兩筆**不同的訂單**會被當
   重複，第二筆悄悄被丟掉。糟糕的是沒人會通知你 — 沒有 log、沒
   有提醒，那筆訂單就這樣不見了。
2. **SQL injection。** 那行 `INSERT` 用 f-string 拼 SQL。如果有人
   把 `user_id` 設成 `Robert'); DROP TABLE scores;--`，就是教科書
   級 SQL injection。（順便：如果 `score` 不是數字，連引號都會壞
   掉。）
3. **`total` 浮點誤差會累積。** 每跑一筆 event 就把 `score × 0.1`
   加到 `total`。電腦其實沒辦法精準表示 0.1，每筆都有一點點誤差，
   跑幾千筆下來會疊起來。最後 `total` 跟你「拿計算機從頭加一遍」
   會對不上。差多少要不要在意，看你 `total` 拿來幹嘛 — 如果是
   loyalty 點數，沒差；如果是要跟財務系統對帳，那就出事。
4. **Retry 沒退避、固定連發 10 次。** 下游 API 真的掛掉的時候，
   這段 code 會對每筆 event 連發 10 次。人家正在燒，你還拼命往
   裡面送。完全反方向。
5. **`conn.commit()` 在 loop 外面。** 一旦中途 crash，整個 batch
   都沒存到。處理到第 9,999 筆掛掉，前面 9,999 筆全沒了，下次從
   零開始。實務上會 per-event commit 或設 checkpoint，crash 後保
   留部分進度。

## 你會看到什麼

LLM 輸出是隨機的，你的 run 不會跟我們完全一樣。但跑個幾次，大致
會看到這個 pattern：

| Bug | Claude 單跑 | Codex 單跑 |
|---|---|---|
| 1. Dedup key | 通常抓到 | 偶爾抓到 |
| 2. SQL injection | 抓到 | 抓到 |
| 3. Float 累積 | 偶爾抓到 | 很少抓到 |
| 4. Retry 無退避 | 抓到 | 偶爾抓到 |
| 5. Commit 在 loop 外 | 偶爾抓到 | 通常抓到 |

跑幾次的整體感覺：

- **單家平均抓到 5 個中 3 個。** 偶爾 4 個，極少 5 個全中
- **兩家合起來抓到 4-5 個** — 但每家貢獻的具體是哪個 bug 不
  穩定
- **兩家風格不一樣。** Claude 偏向過度提醒（會建議一些防禦性
  檢查，其實不算 bug）；Codex 較簡短直接，偶爾完全漏掉 #3 或 #4

重點**不是** Claude 比 Codex 強或反過來。重點是：**一家 review 只
是一次從雜訊裡抽樣**。抽兩次圖像就會變；抽三次（下一章）再變一次。

## 為什麼用兩家就好?

兩家還是會共同的盲點。它們的訓練資料其實有大量重疊，所以當它們一起
漏掉某個東西，往往就是漏掉**同一個東西**。而且當兩家有共識的時候，
沒有第三家可以打破共識。

還有規模的問題。本章故意做小case：28 行、5 個 bug、好理解。但真正需要
這個方法的計劃不是 28 行 — 是一整個架構、一條 pipeline、一個部署
策略。模型差異在那種規模上才看得清楚，而且那種規模上的問題往往不
是「某一行 code 寫錯」這麼單純。

[Chapter 2](../02-the-five-frame/README.zh-TW.md) 會介紹 prompt
結構，讓第三家不是只多一份輸出，而是真的多一份新的 finding。
Chapter 4（BigQuery pipeline）和 Chapter 5（Cloud Run 部署）會用
真實的工程計劃把整套方法跑一遍，你就會看到延展性。

[← 回到 README](../README.zh-TW.md) · [English](./README.md)
