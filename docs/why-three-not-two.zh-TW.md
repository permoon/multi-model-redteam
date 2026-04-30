# 為什麼三家 model 不是兩家？

很自然的問題：如果 multi-model review 比 single-model 好，為什麼是
三家？兩家不行嗎？五家不更好？

## 兩家的「塌陷」問題

兩家 model 跑完，consolidation 出來只有兩種結果：

- **兩家都同意** — 算 consensus
- **只有一家找到** — 算 unique

這是 binary signal，沒有中間值。而且當兩家對某件事意見不同的時候，
你沒有第三個聲音來打破共識，等於回去丟硬幣。

兩家也是 unique finding 最難解讀的地方。當 1/2 抓到某個東西，可能
是那家的 insight、也同樣可能是它的 hallucination。三家的時候，同樣
是 1/3，雖然還是有不確定性，但另外兩家的 review 都沒 flag 這個東
西 — 你有更多 context 可以判斷它是不是真的。

## 三家多出來的價值

三家的 gradient 才有意義：

- **三家都同意**（3-way consensus）— 最強訊號，幾乎肯定值得修
- **三家中的兩家同意**（2-way consensus）— 強訊號，很可能真的有
  問題，另一家可能用了不同角度看
- **只有一家抓到**（unique）— 最有趣的情況。可能是那家的 insight、
  也可能是另外兩家的盲點

3-way / 2-way / 1-way 這個 gradient 就是整個方法的關鍵。「1 of 3」
的 finding — 只有一家抓到的那些 — 才是你會在 single-model review
完全錯過的東西。

## 為什麼不是四家或更多？

兩個原因。

**成本。** 每多一家 model，API 費用大概線性增加。3 家加到 4 家就
是 33% 的成本上升，而且你會跑很多次。邊際價值掉得很快。

**Echo chamber（回音室）。** 這個更重要。現在的前沿 LLM 都是
transformer、都從重疊的公開語料學出來，所以它們共享盲點 — 而當它
們一起漏掉某個東西，常常是漏掉**同一個東西**。多加一家相同架構家族
的 model（再一個 GPT 系列、再一個 fine-tune 過的 open weights）只
是增加票數，沒增加實質多樣性。真的想要第四家，比較合理的選擇是
換**架構真的不一樣**或訓練語料明顯不同的 model，而不是換個 vendor
換個 logo。

實務上，三家 — Claude / Codex (GPT 系列) / Gemini — 已經給你三組
不同 team 的訓練資料、三套不同的 RLHF 偏好、三組不同的盲點。這個
組合足以讓有意義的分歧浮上來。超過三家，收益會很快遞減。

## 三家不夠的時候怎麼辦

如果你發現三家 model 老是一起漏掉某類 bug，解法不是加第四家，而是
加 feedback loop：把人類發現的 bug 累積成 regression 清單、餵回
consolidation prompt，讓系統從你手動抓到的 miss 持續學。
[Chapter 06](../06-going-further/README.zh-TW.md) 的 pitfalls 段
有完整討論（找「echo chamber」那段）。

[← 回到 README](../README.zh-TW.md)
