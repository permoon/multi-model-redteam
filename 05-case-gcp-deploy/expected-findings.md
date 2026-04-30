---
case: "gcp-deploy"
run_at: "2026-04-30T01:47:33Z"
plan_file: "05-case-gcp-deploy/plan.md"
models:
  claude:
    cli_version: "2.1.114 (Claude Code)"
    model: "as configured (default)"
    flags: "--print"
  codex:
    cli_version: "codex-cli 0.125.0"
    model: "gpt-5.5 (medium reasoning)"
    flags: "exec --skip-git-repo-check"
  gemini:
    cli_version: "0.36.0"
    model: "as configured (default)"
    flags: "(stdin, no flag)"
timeout_sec: 600
notes: |
  Output is non-deterministic. Findings below are from THIS specific run on
  2026-04-30; your output may differ in wording but should match the
  pattern: ~9 consensus findings, ~17 unique findings (split across 3
  teams), ~2 triple-blind-spot items, plus disagreements and coverage gaps.

  This run captured 6 of the 7 deliberately seeded flaws fully and 1
  partially (per the chapter README):
    1. roles/editor over-scoping              → C3 (Claude + Codex + Gemini)
    2. Cloud Run/Workflows region mismatch    → A4 (Claude only — Gemini's
                                                 Rollback B touches the
                                                 split-brain side but does
                                                 not reach latency budget)
    3. FIRESTORE_PROJECT hardcoded to prod    → M1 (Claude only)
    4. Workflows without retry policy         → C5 + Gemini Hidden B
                                                 (timeout asymmetry angle)
    5. minScale=0 vs 500ms p95 SLO            → C2 (Claude + Codex + Gemini)
    6. No rollback strategy                   → C9 + R1 + R4 + Codex
                                                 Rollback R1
    7. `:latest` image tag                    → C1 (Claude + Codex + Gemini)

  Highlights:
  - A1 (OIDC `audience` missing) — found by Claude only — is the chapter's
    centerpiece unique finding. Cloud Run private services require ID
    token audience = service URL; without it, the first hour of cutover
    returns 401 across the board. Codex and Gemini both reviewed the same
    OIDC config block and missed this concrete trap.
  - Gemini Hidden B — Workflow 30s default HTTP timeout vs Cloud Run 300s
    default request timeout creates "ghost executions": Workflow times
    out and retries, while Cloud Run continues processing the original
    request. Pure GCP-native infra trap; Claude and Codex missed it.
  - Plan v3 §1271 predicted "Gemini strongest on #2 (GCP home turf,
    region mismatch)". Actual: Gemini did not catch region mismatch;
    Claude did. A useful reminder that even a model's "expected
    strength" is not deterministic — which is why we run multi-model.
---

## Consensus Findings (mentioned by ≥ 2 teams)

### C1. `:latest` image tag = 不可預測 rollback / staging-prod drift
**Teams:** Claude (A2, M4) / Codex (Hidden A1) / Gemini (Rollback A)
- **TRIGGER:** Mutable tag。deploy 後 image digest 與 staging 驗證版本不保證一致；CI 在 staging 驗證和 prod cutover 之間 push 新 image；rollback 切回「舊 revision」實際上仍指向同一 mutable tag。
- **IMPACT:** Codex「Prod runs unvalidated code... duplicate writes, malformed Pub/Sub events, 5xx spikes」；Claude「rollback 結果不確定，1-2 週後才發現『為什麼修了沒效』」；Gemini「the `latest` tag in the registry is now 'poisoned'」。
- **DETECTABILITY:** Codex「5-15 minutes if traffic is high; hours off-peak」。
- **Why it matters:** 三隊一致提議 image tag 用 git SHA / immutable digest。這是 cutover 前阻塞級別的修法，沒做的話後續所有 rollback runbook 都失效。

### C2. Cold start with `minScale: 0` 必破 500ms SLO
**Teams:** Claude (A3) / Codex (Hidden A3) / Gemini (Hidden A)
- **TRIGGER:** ~15 min idle 後 scale to zero；下次 hourly 第一個 request 觸發冷啟。
- **IMPACT:** Claude「Node + 50 Firestore reads warmup 2-5s」；Gemini「Node.js Express apps with Firestore/Pub/Sub clients often take 2s–5s to initialize... downstream consumers (expecting 1s max) will timeout and potentially trigger their own retry storms」。
- **DETECTABILITY:** Immediate at top of hour，但需 p95/p99 by minute 才看得見（Codex「only if p95/p99 latency is monitored by minute」）。
- **Why it matters:** 三隊一致 `minScale=1`。Claude 估 ~$15/月。沒修的話「每小時第一批 request 必 timeout」（Claude）。

### C3. `roles/editor` SA = 整個 project blast radius
**Teams:** Claude (D1) / Codex (Rollback R3) / Gemini (Misuse B)
- **TRIGGER:** SSRF / 依賴 RCE / token 洩漏 / log 誤輸出 token。
- **IMPACT:** Gemini「permission to delete the entire project, including the Firestore database and Artifact Registry」；Claude「攻擊者可刪除整個 Firestore database、改 Pub/Sub 訂閱、推 image 進 Artifact Registry 觸發供應鏈」；Codex「The service can modify unrelated resources, read sensitive data, or destroy infra」。
- **DETECTABILITY:** Hours-days；Codex 補強「page on IAM changes, service deletion, storage access」。
- **Why it matters:** 三隊一致改 `roles/datastore.user` + `roles/pubsub.publisher`。**Cutover 前阻塞級別的安全硬傷。**

### C4. 並行批次（手動 curl + scheduled run / Scheduler retry overlap）
**Teams:** Claude (M2, D2) / Codex (Misuse M1, Hidden A2) / Gemini (Misuse A)
- **TRIGGER:** Oncall「check if it works」手動 curl /batch；Scheduler retry；workflow 跑超過 60 min。
- **IMPACT:** Gemini「duplicate documents in Firestore and double-notifying downstream consumers」；Codex「Duplicate processing and duplicate Pub/Sub messages」；Claude「下游 user 收到雙通知」。
- **DETECTABILITY:** Gemini「5-day detection. Usually caught when a downstream user complains」；Codex 給具體 alert：「more than 1 active execution」、「executions start less than 55 minutes apart」。
- **Why it matters:** Mitigation 三隊有共識（distributed lock / idempotency key / Firestore transaction lease），但細節不同。

### C5. 缺 idempotency → Pub/Sub 重複發布不可回滾
**Teams:** Claude (D2, B3, R5) / Codex (Hidden A4, Rollback R2) / Gemini (Misuse A 隱含)
- **TRIGGER:** Scheduler retry / operator 手動 / RSS GUID 重發 / cold start timeout 觸發 retry。
- **IMPACT:** Claude「下游 side effect（user 通知、計費、外部 webhook）已執行；無法 undo」；Codex「inflated downstream counts... duplicate work and costs」。
- **DETECTABILITY:** Codex「5-minute detection if duplicate event IDs are measured; 5-day detection likely comes from customer reports」。
- **Why it matters:** 三隊一致：article GUID 當 Firestore doc id（natural idempotency）+ Pub/Sub `event_id = guid` + 下游 dedup TTL。Codex 給具體閾值（`duplicate event IDs > 100 in 10 minutes`）。

### C6. 上游 RSS 慢 / Slowloris-style 「tarpit」 → 並發飽和、帳單爆
**Teams:** Claude (D3, B1) / Codex (Dep D1, Boundary B4) / Gemini (Dep A)
- **TRIGGER:** Claude「某 RSS server 變慢到 30s」；Gemini「responds at 1 KB/s instead of failing」；Codex「200 QPS while each request does 50 Firestore reads」。
- **IMPACT:** Gemini「scale up to maxScale: 100, burning budget rapidly while still returning 504s」；Claude「maxScale=100 × 1Gi 一路衝高，當月帳單意外」。
- **DETECTABILITY:** Instance_count 曲線會跳但無 alert。Gemini 給具體偵測：「`instance_count > 50` AND `throughput < 10 req/sec`」。
- **Why it matters:** 三隊都建議 per-feed timeout（Claude 5s）。Claude 唯一給 maxScale 容量公式（建議 maxScale=10）。

### C7. 大 / 惡意 RSS payload → OOM
**Teams:** Claude (B4 部分) / Codex (Boundary B2, B3) / Gemini (Boundary A)
- **TRIGGER:** Codex「50k items, very large XML document」；Gemini「200MB XML payload or highly nested tags」（billion laughs）；惡意 entity / script tag。
- **IMPACT:** Gemini「Container Terminated due to OOM... killed by the runtime (Signal 9)」；Codex「Workflows may retry the whole batch, amplifying load」。
- **DETECTABILITY:** 5 min via `memory/utilizations > 85%` 或 log-based metric `unclean signal 9`。
- **Why it matters:** 一致建議 payload size cap、parser 限欄位長度（Codex「title > 500 chars, url > 2048, description > 10000」）。

### C8. Pub/Sub publish 失敗路徑沒寫 → 靜默資料缺口
**Teams:** Claude (D4) / Codex (Dep D3, Rollback R5) / Gemini (Boundary B)
- **TRIGGER:** Pub/Sub 區域故障、IAM 漏改、quota 用罄。
- **IMPACT:** Claude「Firestore 寫入成功但 Pub/Sub 發布失敗 = 資料寫了但下游永遠不知道，永久不一致... 下游 backlog 不會增加（因為根本沒發），現有 backlog alarm 完全偵測不到」（最致命的偵測盲點）；Codex「Historical news notifications are missing」。
- **DETECTABILITY:** 5-day（Codex「5-day detection if only content freshness reveals the gap」）。
- **Why it matters:** 一致建議 reconciliation metric：`articles_written_count` vs `pubsub_messages_published_count`，Codex「mismatch exceeds 1 article for any completed hourly batch after 10 minutes」。Claude 提出 outbox / 寫入順序倒置（先 Pub/Sub 後 Firestore，accept duplicates）。

### C9. Rollback 到 GKE 雙寫條件 + 缺 runbook
**Teams:** Claude (M3, R2) / Codex (Misuse M3, Rollback R4)
- **TRIGGER:** Claude「切回 GKE 時只停 Cloud Run；Workflow 仍呼叫舊 Cloud Run URL（404）或舊 GKE Cron 也跑、Cloud Run 也跑 = 雙觸發」；Codex「LB routes traffic back to GKE but Cloud Scheduler/Workflows still calls Cloud Run /batch」。
- **IMPACT:** 雙寫資料事故、metric 混亂、Workflows error email 雜訊。
- **DETECTABILITY:** Codex「Minutes if source labels exist; otherwise hard to diagnose」。
- **Why it matters:** Codex 提具體偵測（每筆 write/publish 加 `producer_runtime=gke|cloud-run`）；Claude 補 GKE warm 1 週對月結邏輯太短（M3）。**Gemini 完全沒覆蓋這條 — 雙隊一致已是強信號。**

---

## Unique Findings (mentioned by 1 team)

### Claude only
- **A1: OIDC `audience` 缺漏 → 第一次呼叫 401。** Cloud Run 私有服務要求 ID token 的 audience = service URL。**這是個會直接讓 cutover 第一個小時全失敗的硬傷，Codex / Gemini 都沒指出 — 兩種解讀：(a) Claude 看到別人沒看到的具體配置陷阱；(b) Claude 對 GCP OIDC 細節有額外經驗。建議當作真實風險處理。**
- **A4: 跨 region us-east1 ↔ us-central1 把 SLO 預算吃光。** Workflows ↔ Cloud Run 30ms RTT + Firestore nam5 跨區讀 50 docs ~250ms。Gemini 的 Rollback B（Regional Split-Brain）摸到邊但沒走到延遲預算這層。
- **B2: Article body > 1MB → Firestore 1MB hard limit 拒寫，靜默丟資料。**「log 有但無 alert；可能永不被發現」。具體且可量化。
- **M1: `FIRESTORE_PROJECT: "my-prod-project"` 硬編碼在 yaml → staging 可能寫 prod。** 對 multi-env 部署的常見陷阱。
- **B4: /batch 單次處理逼近 Cloud Run 300s default timeout。** 5000 articles × 50ms = 250s。
- **R1: 沒 canary，0→100% 一次切換。** 「Cut production traffic at the load-balancer level next Tuesday morning」一刀切。
- **R3: 監控段落沒任何具體 alert 閾值。** Claude 唯一給整套具體閾值表（5xx > 1%/5min PagerDuty、p95 > 800ms/10min email、instance_count > 30/15min email、Workflows 連續 2 次 failure page、log-based `INVALID_ARGUMENT OR DEADLINE_EXCEEDED` > 5/min email）。
- **R4: Firestore 寫入不可回滾。** schema bug 寫入後 rollback Cloud Run 救不回壞資料。

### Codex only
- **Hidden A4: Firestore reads 假設 fresh enough → 多 instance 並發讀 dedupe marker。** Read-after-write consistency 問題。其他兩隊聚焦 retry idempotency，沒走到並發讀 dedupe key 這層。
- **Boundary B1: 空 RSS feed 處理。** 「normally active feed has 0 articles_seen for 3 consecutive hourly runs」可能被當正常吞掉。
- **Misuse M2: cutover 在 IAM/URL 還沒對齊就發生。** 「Ad-hoc traffic may work if public/LB path differs, but scheduled batch fails with 401/403/404」— 部分成功遮蔽問題。
- **Misuse M4: staging 不等於 production，要 shadow-run gating。** 「Block if Cloud Run differs by > 5% article count or has publish_success_rate < 99.9%」。最具體的 cutover gate 提議。
- **Rollback R1: 新版 Cloud Run 寫壞 Firestore canonical URL / article ID / dedupe key。** 「Rolling traffic back to GKE does not remove corrupted data」。Claude R4 摸到邊，但 Codex 點出具體污染欄位。
- **Dep D2: Firestore quota 退化 / index contention 的放大效應。** 「Every request reads ~50 docs, so small Firestore latency increases multiply」— 50× latency multiplier 是其他兩隊沒展開的。

### Gemini only
- **Hidden B: Workflow ↔ Cloud Run timeout 不對稱 → ghost executions。** 「Cloud Workflows has a default HTTP timeout (often 30s)... Cloud Run instance continues processing in the background (as it has its own 300s default timeout). This leads to 'ghost' executions and duplicate Pub/Sub messages if the workflow retries」。**這個具體的 timeout 不對稱沒人提，是 Gemini 唯一獨到 insight。**
- **Dep B: Artifact Registry regional outage。** 「`minScale` is 0, Cloud Run must pull the image at the start of the hourly batch... migration from GKE (which might have had the image cached on nodes) makes this a hard failure」— GKE→Cloud Run 在 image cache locality 上的差異，其他兩隊沒看到。
- **架構建議：REJECT `/batch` internal fan-out**（見下「Apparent Disagreements」）。

---

## Apparent Disagreements

### D1. /batch 架構是否保留
- **Gemini** 明確 **REJECT**：「`/batch` internal fan-out: A single HTTP request doing all the work is prone to timeouts. Use Workflows to iterate over a list of feeds and call a single `/process-feed` endpoint per item to distribute the load and handle timeouts individually」。
- **Claude / Codex** 接受 /batch 架構，提議內部加 idempotency lock、per-feed timeout、payload limit、batch 拆 paginated。
- 影響面：Gemini 路線改架構（每 feed 失敗獨立、爆破半徑小、但工程量大、Workflows 步驟數變多可能撞 Workflows 自身 limits）；Claude / Codex 路線加護欄（工程量小、但 single-request 失敗模式仍在）。**人類決定。**

### D2. maxScale 容量規劃
- **Claude** 主張 `maxScale=10`，附公式（200 QPS × 0.5s / 80 ≈ 2 instances 穩態，10 給 5x 尖峰 buffer）。
- **Codex / Gemini** 沒給具體數字，只 alert 在撞 maxScale=100 上限。
- 不算嚴格 opposite，但留兩條路：縮 maxScale 防失控成本（Claude）vs 維持 100 但加 alert（Codex/Gemini）。

---

## Coverage Gaps

5 個 dimension 整體都有兩隊以上覆蓋，沒有任何 dimension 完全空白。但下列**子題**只有單隊或無人提：

1. **Pre-cutover validation / shadow-run gating**：只 Codex Misuse M4 提具體 gate 閾值；Claude R4 弱提（「shadow collection 比對 1 天再切」）；Gemini 無。
2. **OIDC audience config**：只 Claude A1。Cloud Run 私有服務的常見坑，覆蓋過薄。
3. **Cross-region 設計**：只 Claude A4 + Gemini Rollback B（部分）；具體 mitigation（Workflows 移 us-central1）只 Claude。
4. **Cost / budget alert with $ threshold**：三隊都沒提具體美元閾值的 budget alert。Claude 只說「當月帳單意外」「billing alert 月底才響」，沒落到 GCP Budget API alert 設定。
5. **Schema migration / 跨 producer-consumer 的 message contract versioning**：Claude R4 / Codex Rollback R1 都摸到「壞資料 rollback 不掉」，但都沒走到「Pub/Sub message schema 演進對既有 subscriber 的影響」這層。

---

## Triple Blind Spot

保守只列我有把握的：

### TBS1. Backfill / catchup procedure 完全缺
三隊都沒問：**「如果 Cloud Run 掛 4 小時，怎麼補回 4 個 hourly batch?」** 直接重觸發會把 4 小時的內容一次 flood 下游 Pub/Sub（C5 的反向放大，下游若做 idempotency 就靠它，沒做就災難）；不重觸發則永久錯過該時段新聞。所有 cutover 計畫都應該有「missed batch backfill SOP」+「下游能否吃下 4x burst 的 capacity 確認」。這是 ops day-1 必遇問題。

### TBS2. Pub/Sub Dead-Letter Queue / 消費端失敗回流
三隊都聚焦在 publisher 側（C8 publish 失敗、C5 重複發布），**完全沒人提 Pub/Sub subscription 的 DLQ 設定**：當下游 subscriber 持續 nack 時訊息該流到哪？Pub/Sub 預設無限 redelivery 直到 acknowledgement deadline 累積。這會讓 C5（duplicate flood）的影響面從「一次性下游雙通知」變成「持續 redelivery 直到 subscriber 手動清 backlog」。reconciliation metric（C8 mitigation）若不結合 DLQ 設定就只是事後對帳，沒有自動化 contain 機制。
