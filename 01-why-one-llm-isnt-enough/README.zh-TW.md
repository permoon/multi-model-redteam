# Chapter 01 — 為什麼一家 LLM 不夠

你已經在用 Claude Code（或 Cursor、Codex CLI）review code。它能抓到
很多東西。為什麼還要再加第二家、甚至第三家？

這一章是最便宜的答案：28 行 Python、5 個刻意藏的缺陷、兩家單一 model
review 並排比對。60 秒可以自己跑一次。

## 檔案

- [`target-code.py`](./target-code.py) — 28 行 Python script，藏 5 個
  設計缺陷（不在 code 裡留註解，所有缺陷只列在本 README）
- [`compare-models.sh`](./compare-models.sh) — 順序跑 Claude → Codex，
  分別存到 `review-claude.md` / `review-codex.md`

## 怎麼跑

```bash
cd 01-why-one-llm-isnt-enough
bash compare-models.sh
# → review-claude.md
# → review-codex.md
```

費用：約 $0.02（兩家對 28 行 code 各跑一次）。

跑完讀兩個檔，對照下面 5 個預期缺陷。

## `target-code.py` 藏的 5 個缺陷

Code 是「訂單計分批次」 — 讀 events、按 user dedup、寫一筆計分到
SQLite、累加 loyalty total 推給下游 API。

1. **Dedup key 只用 `user_id`** — 同人下兩筆不同訂單會被當重複，
   第二筆被靜默丟掉
2. **SQL injection（f-string 拼接）** — `INSERT INTO scores VALUES
   ('{e['user_id']}', {e['score']})` 是教科書級 SQLi（順帶 `score`
   非數值時還會 quoting bug）
3. **`total` 浮點誤差累積** — `total += e["score"] * 0.1` 跨 N 個
   事件累加，IEEE-754 誤差會疊加。後果嚴重度取決於 `total` 在下游
   做什麼
4. **Retry 無退避、固定 10 次** — 下游真出事時，每個 event 都連發
   10 次，放大故障；該退讓的時候反而火上加油
5. **`conn.commit()` 在 loop 外** — 中途 crash 整批沒保存。應該
   per-event commit 或顯式 transaction / checkpoint 策略

## 你會觀察到什麼

Model 輸出有隨機性，所以你的具體 run 可能不同。典型 pattern：

| 缺陷 | Claude 單跑 | Codex 單跑 |
|---|---|---|
| 1. Dedup key | 通常抓到 | 偶爾抓到 |
| 2. SQL injection | 抓到 | 抓到 |
| 3. Float 累積 | 偶爾抓到 | 很少抓到 |
| 4. Retry 無退避 | 抓到 | 偶爾抓到 |
| 5. Commit 在 loop 外 | 偶爾抓到 | 通常抓到 |

跑個兩三次通常會看到：

- **單家平均抓到 5 個中 3 個**
- **兩家合起來抓到 4-5 個** — 但每次缺的不一定同一個
- **兩家風格不同** — Claude 偏向過度提醒（會建議一些不算 bug 的防禦
  性檢查）；Codex 較簡短，偶爾完全漏掉 #3 或 #4

重點**不是**「Claude > Codex」或反過來。重點是**單一 review 只是
一次從雜訊分布抽樣**。抽兩次圖像已經改變；下一章再抽一次又再變一次。

## 為什麼不停在兩家就好？

兩家仍有共同盲點：

- 兩家都是 transformer + 都 train 在重疊的公開語料，所以常常一起
  漏掉相同的 concurrency / consistency / IAM pattern
- 兩家有共識時，沒有第三家可以打破共識（萬一兩家都錯）
- 這個不對稱性在**架構級別的 plan** 上最明顯（本章故意只用 code-level
  小範例好快速跑） — chapter 04（BigQuery pipeline）和 05（Cloud Run
  部署）的真實案例會把這放大

[Chapter 02](../02-the-five-frame/README.zh-TW.md) 介紹的 prompt
frame 讓第三家不是只多一份輸出，而是真的多一份訊號。

[← 回到 README](../README.zh-TW.md) · [English](./README.md)
