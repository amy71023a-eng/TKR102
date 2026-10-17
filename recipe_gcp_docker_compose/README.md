# Recipe Collections V11

V11 是正式整合版：以 permission-safe Docker / crawler / proxy 架構為主，整合 V10 的正規化、MySQL ER Model、營養計算、Flask API 與 Hermes API，並包含**價格模組（`python/Price`）**，將賣場價格回填至食品營養表，供 API 一併回傳熱量與預估價格。

## 模組分工

| 模組 | 說明 |
| :--- | :--- |
| Crawler / Proxy / Mongo Writer | 食譜爬取、Kafka 分流、寫入 MongoDB（`recipe_ai.raw_recipes`） |
| ETL 01~09 / `10_pipeline.py` | 資料正規化、營養計算、匯入 MySQL |
| **價格模組（`python/Price`）** | **抓取賣場價格、換算每 100g 價格、回填食品營養表** |
| Flask API / Hermes API | 對外提供食譜查詢與推薦服務 |
| 網頁端 | 不包含在本專案；由另一位組員透過 Flask API 獨立開發 |

## 正式資料流

```text
Airflow
  -> crawler_jobs (5 partitions)
  -> crawler-direct + 4 proxy workers
  -> ytower_recipe_results
  -> mongo-writer
  -> MongoDB recipe_ai.raw_recipes
  -> ETL 01~09 / 10_pipeline.py
  -> MySQL recipe_ai
  -> Flask API / Hermes

Airflow（價格模組排程）
  -> 賣場價格抓取與比對
  -> 重量擷取、換算每 100g 價格
  -> 回填食品營養表
  -> （供 Flask API / Hermes 一併取得熱量與價格）
```

## V11 核心變更

- 單一 `crawler_jobs` Topic，5 partitions / 同一 crawler consumer group。
- 1 個 Direct Worker + 4 個動態 TW Proxy Workers。
- Result Topic 統一為 `ytower_recipe_results`。
- Mongo Writer 寫入 `recipe_ai.raw_recipes`，以 `SEQ` idempotent upsert。
- Docker runtime data 改用 named volumes，不再 chown Git source tree。
- MySQL / MongoDB application service 使用 application user，不使用 root。
- Airflow 拆為 init / webserver / scheduler，DAG 串完整 crawler -> MongoDB -> ETL -> MySQL。
- 修正 Direct Worker job failure offset 風險。
- `published_date` 正式匯入 MySQL。
- 食材 canonical name 移除尾端「約」。
- Direct crawler 補 Browser headers。
- `MAX_POLL_INTERVAL_MS` 預設提高為 16 小時。
- `HERMES_API_KEY` 設定後會實際驗證，原 `{items:[...]}` response 契約保持不變。
- 網頁端不包含在本專案；網頁由另一位組員透過 Flask API 獨立開發。

## 價格模組（`python/Price`）

價格模組負責為食譜食材補上價格資訊，讓下游服務能在同一張食品營養表中同時取得熱量與價格。

### 處理流程

1. 從賣場網站抓取與食譜食材對應的品名與商品網址。
2. 擷取商品重量，並換算為每 100g 價格。
3. 將結果回填食品營養表。
4. 讓後續流程可在同一張表一併取得熱量與價格。

### 部署與排程

- 部署於 GCP VM。
- 以 Docker 容器化執行。
- 由 Airflow 控制排程。

### 開發過程遇到的問題與改善

| 問題 | 改善方式 |
| :--- | :--- |
| 價格比對結果偏少 | 增加品名關鍵字相似度；仍未比對到品名時，改用站內搜尋 |
| 比對到非食品類商品 | 排除非食品類關鍵字或商品類型 |
| 網頁缺少重量資訊 | 優先擷取網頁商品名稱中的重量；若抓不到，再讀取網頁規格欄位中的重量 |

### 與下游的資料約定

價格資料不完整時，API 以 `price_status` 標示（例如 `PARTIAL`）；缺少價格的食材顯示「未提供」，不以 0 填補。

## 啟動

```bash
bash scripts/bootstrap-env.sh
bash scripts/first-start.sh
```

或自行：

```bash
cp .env.example .env
# 修改所有 CHANGE_ME_* secrets
docker compose --env-file .env up -d --build
```

## Docker 內部連線

- MySQL: `mysql:3306`
- MongoDB: `mongodb:27017`
- Kafka: `kafka:9092`
- PostgreSQL: `postgres:5432`

Host 預設：MySQL 3307、MongoDB 27018、Kafka 9094、Airflow 8080、Flask 5001。

## API

V10 已正式加入的 API 在 V11 全部保留：

- `GET /health`
- `GET /api/v1/recipes`
- `GET /api/v1/recipes/search`
- `GET /api/v1/recipes/random`
- `GET /api/v1/recipes/{seq}`
- `GET /api/v1/categories`
- `POST /api/v1/categories/resolve`
- `POST /api/v1/recommend`
- `POST /api/v1/hermes/recommend`

## 文件

- `docs/V11_ARCHITECTURE.md`
- `docs/V11_INTEGRATION_FIXES.md`
- `docs/V11_FORMAL_VALIDATION.json`
- `docs/er_model.dbml`

舊 V9 Multi-NIC / V10 crawler 元件已移入 `legacy/`，不再由 active compose 使用。
