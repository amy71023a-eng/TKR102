# TKR102｜雲端資料工程師養成班 專題作品集

## 今天吃啥咪：食譜 AI 推薦系統（團隊專題）

使用者可在 LINE Bot 或網頁輸入想吃的食材、不吃的食材與熱量限制，系統會推薦食譜，並提供熱量與預估食材價格。

專題以資料工程流程為核心：自動爬取食譜與賣場價格、清洗正規化後存入資料庫，再由 Flask API 提供給 LINE Bot 與網頁使用。整個系統以 Docker Compose 部署在 GCP VM 上，並由 Airflow 排程。


## 系統資料流

```text
食譜爬蟲 (Kafka + 多 Worker)
  -> MongoDB 保存原始資料
  -> ETL 清洗與正規化
  -> MySQL
  -> Flask API
  -> LINE Bot / 網頁

價格模組（Airflow 排程）
  -> 賣場價格抓取與比對
  -> 換算每 100g 價格
  -> 回填食品營養表
```

## 技術棧

Python、GCP（VM）、Docker / Docker Compose、Airflow、Kafka、MongoDB、MySQL、Flask API、Git

## 團隊分工

| 模組 | 負責內容 | 負責人 |
| :--- | :--- | :--- |
| 食譜爬蟲與資料寫入 | Kafka、Proxy Worker、MongoDB | <組員> |
| 資料正規化與 ETL | 食材清洗、營養計算、匯入 MySQL | <組員> |
| **價格模組** | **賣場價格抓取、重量換算、回填營養表** | **我** |
| API 與 LINE Bot | Flask API、Hermes 整合 | <組員> |
| 網頁端 | 透過 Flask API 開發 | <組員> |

## 我的貢獻：價格模組

我負責為食譜食材補上價格，讓後續流程能在同一張食品營養表中一併取得熱量與價格。

- 從賣場網站抓取與食譜食材對應的品名與商品網址
- 擷取商品重量，換算為每 100g 價格
- 回填食品營養表
- 部署於 GCP VM，以 Docker 容器化，由 Airflow 控制排程

**開發過程中遇到的問題與改善：**

| 問題 | 改善方式 |
| :--- | :--- |
| 價格比對結果偏少 | 增加品名關鍵字相似度；仍未比對到時改用站內搜尋 |
| 比對到非食品類商品 | 排除非食品類關鍵字或商品類型 |
| 網頁缺少重量資訊 | 優先擷取商品名稱中的重量；抓不到再讀取規格欄位 |

詳細說明請見：[價格模組 README](recipe_gcp_docker_compose/python/Price)

## 專案程式與說明

- 整合版專案（含啟動方式、API 清單、架構文件）：[recipe_gcp_docker_compose](https://github.com/amy71023a-eng/recipe_gcp_docker_compose)
- 價格模組程式：`recipe_gcp_docker_compose/python/Price`

## 關於我

具備 14 年食品、生技、製藥與醫療器材產業的研發與品保經驗，2026 年完成緯育 Tibame「雲端資料工程師養成班」。希望把品保工作中累積的需求釐清、異常追蹤、根因分析與品質控管經驗，帶入資料管線的設計與維運。
