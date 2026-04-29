# Chapter 01 — 為什麼一家 LLM 不夠

> 🚧 建構中 — 在 Day 6 完成。

## 本章目標

- 跑一次單一 LLM 設計 review（標準工作流）
- 看哪些設計缺陷它漏抓
- 加第二家 model，看分歧出現
- 為第三家鋪陳（chapter 2 介紹 5 點框架）

## 檔案（完成後）

- `target-code.py` — 一段 Python 程式碼，含 5 個設計缺陷（程式碼**不**標註漏洞，
  漏洞清單放在本章 README，不放 code 註解）
- `compare-models.sh` — 順序跑 Claude 然後 Codex，diff 兩家輸出

[← 回到 README](../README.zh-TW.md)
