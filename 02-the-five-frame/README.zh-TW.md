# Chapter 02 — 5 點失敗劇本框架

這章是整個 repo 的方法論核心。後面所有東西都建立在這個框架上，建議
至少細讀一次。

## 檔案

- [`frame.md`](./frame.md) — 完整論述：為什麼是這 5 維度、怎麼校準
  finding、好 vs 壞 finding 怎麼分、10 分鐘 triage rubric。**繁中版**：
  [`frame.zh-TW.md`](./frame.zh-TW.md)
- prompt 本身在
  [`../prompts/system-prompt.md`](../prompts/system-prompt.md)（CC0）

## 你會理解：

1. **為什麼** 這 5 維度抓得到 OWASP / SRE checklist 漏掉的東西
2. **怎麼** 認出一個壞 finding（譬如「加 monitoring」但沒講閾值）
   並把它退掉
3. 一份 **rubric**，在做嚴重度排序前先 triage 每個 finding

## TL;DR

這個框架要求每個設計都要在這 5 個維度上各給**至少 2 個具體**的失
敗劇本：

1. **隱性假設** — 順序、唯一性、原子性、資料新鮮度、呼叫方行為
2. **依賴失敗** — 上下游服務 degrade 或掛掉時會發生什麼事
3. **邊界輸入** — 空、單筆、極大批次、惡意輸入、格式錯誤
4. **誤用路徑** — 呼叫方 / 使用者 / operator 用錯方法
5. **回滾與爆炸半徑** — 怎麼救、出事的話爆炸範圍多大

每個劇本都要含 TRIGGER（觸發條件）、IMPACT（影響）、DETECTABILITY
（多久會被發現）。「加 monitoring」這種沒閾值的 generic 建議會直接
被退掉 — 如果你不能講出哪個 metric、哪個閾值、哪個 alert，那個
finding 還沒做完。

[`frame.zh-TW.md`](./frame.zh-TW.md) 有每個維度的完整推理、校準範
例、10 分鐘 rubric。

[← 回到 README](../README.zh-TW.md) · [English](./README.md)
