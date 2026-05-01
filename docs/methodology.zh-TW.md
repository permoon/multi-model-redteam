# 5 個檢核維度的方法論

![Multi-model 設計紅隊 — 從單一 plan 到 ranked findings 的 4 階段流程，含 consensus / unique / blind-spot 三類](../assets/architecture.png)

當你叫 LLM「review 這份設計」，拿回來的通常是抽象建議 — 「注意 edge
case」、「加 monitoring」、「小心 race condition」。每一條技術上都
對，但實際上幾乎沒用。沒有具體可以動手做的事、沒有 metric 可以拉
alert、沒有具體 scenario 可以驗。

5 個檢核維度的框架就是用來取代這種輸出的。它要求每次 review 都要涵
蓋下面 5 個維度、每個維度至少給 2 個具體的失敗劇本、每個劇本必須含
TRIGGER、IMPACT、DETECTABILITY。這個結構強迫 finding 變成可以動手
做的事：每一條都可以直接寫成 Jira 票，不用再翻譯解讀。

## 5 個維度，一句話講完

1. **隱性假設** — 這份設計依賴哪些沒寫出來的前提（順序、唯一性、
   原子性、資料新鮮度、呼叫方行為）？
2. **依賴失敗** — 上下游 component **degrade**（不是直接掛掉）的
   時候會怎樣？
3. **邊界輸入** — 空、極大、格式錯、惡意；這份設計在 p99 和惡意
   百分位輸入下會怎樣？
4. **誤用路徑** — 如果人（呼叫方、使用者、operator）沒按照 plan
   走會怎樣？
5. **回滾與爆炸半徑** — 出事的時候怎麼救、傷害多大？

## 為什麼是這 5 個

現有的 review 框架要不就是焦點太窄（OWASP 只看 security），要不就
是只能在部署後 fire（SRE Four Golden Signals 只看 operational
health）。5 個檢核維度是為**部署前**這個時間點設計的：設計已經寫
好、code 還沒上線、你想知道接下來會被什麼咬。

我們會收斂到 5 個是因為早期版本有 7 個（compliance 和 observability
是分開的），實務上發現它們幾乎一定跟其他 5 個一起出現，就合併了。
如果你的領域真的需要更多維度 — 譬如有明確 compliance 要求的法規
產業 — fork 這個 prompt 就好，它採 CC0 就是為了讓你能 fork。

## 接下來去哪

- **章節走讀** — [Chapter 02](../02-the-five-frame/README.zh-TW.md)
  是實際把框架應用一次的章節。新手從這裡開始
- **完整論述** —
  [`02-the-five-frame/frame.zh-TW.md`](../02-the-five-frame/frame.zh-TW.md)
  有更深的版本，包括 calibration rubric、好 vs 壞 finding 的具體
  範例
- **Prompt 本身** —
  [`prompts/system-prompt.md`](../prompts/system-prompt.md) 是 CC0
  artifact，要拿去哪用都可以
- **為什麼三家 model 不是兩家？** — 見
  [`why-three-not-two.zh-TW.md`](./why-three-not-two.zh-TW.md)，
  解釋 model 數量的選擇

[← 回到 README](../README.zh-TW.md)
