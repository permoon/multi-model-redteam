# Chapter 02 — 5 點失敗劇本框架

`multi-model-redteam` 的方法論核心。讀完這一章再進下一章前，建議讀兩遍。

## 檔案

- [`frame.md`](./frame.md) — 完整方法論論述（5 維度、為什麼是這 5 點、校準、
  好 vs 壞 finding、10 分鐘 rubric）。**繁中版**：[`frame.zh-TW.md`](./frame.zh-TW.md)
- prompt 本身在 [`../prompts/system-prompt.md`](../prompts/system-prompt.md)（CC0）

## 你會帶走的

1. **為什麼** 5 維度框架抓得到 OWASP / SRE 漏掉的東西
2. **怎麼** 認出壞 finding（「加 monitoring」）並拒絕
3. 一份 **rubric** 在嚴重度排序前 triage finding

## TL;DR（給沒耐心的）

這個框架要求每個設計都要：

1. **隱性假設** — 順序、唯一性、原子性、新鮮度、呼叫方行為
2. **依賴失敗** — 上下游 degrade 模式
3. **邊界輸入** — 空、巨大、malformed、malicious
4. **誤用路徑** — 呼叫方 / 使用者 / operator 用錯
5. **回滾與爆炸半徑** — 怎麼救、傷害多大

每個維度至少 2 個具體劇本，每個劇本要含 TRIGGER、IMPACT、DETECTABILITY。
Generic advice（「加 monitoring」）會被明確拒絕。

讀 [`frame.zh-TW.md`](./frame.zh-TW.md) 了解每個維度的存在理由、校準範例、
10 分鐘 rubric。

[← 回到 README](../README.zh-TW.md) · [English](./README.md)
