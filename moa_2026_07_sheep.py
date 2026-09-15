"""從農業部 SheepQuotation API 抓取資料並輸出為 JSON 檔。"""

import json
import ssl
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


# 要查詢的日期區間；可依需求修改。
START_TIME = "2026/07/01"
END_TIME = "2026/07/31"

# API 位址與輸出檔案位置。
API_URL = "https://data.moa.gov.tw/api/v1/SheepQuotation/"
OUTPUT_PATH = Path(__file__).with_name("moa_2026_07_sheep.json")


def main() -> None:
    # 將日期參數進行 URL 編碼，組成完整 API 請求網址。
    query = urlencode({"Start_time": START_TIME, "End_time": END_TIME})
    request = Request(
        f"{API_URL}?{query}",
        headers={"accept": "application/json"},
    )

    # 該 API 的憑證缺少 Subject Key Identifier。新版 Python 預設會嚴格檢查
    # 此欄位，因此僅關閉這一項額外檢查；仍保留一般 HTTPS 憑證鏈驗證。
    ssl_context = ssl.create_default_context()
    if hasattr(ssl, "VERIFY_X509_STRICT"):
        ssl_context.verify_flags &= ~ssl.VERIFY_X509_STRICT

    # 呼叫 API 並將回應文字轉為 Python 字典。
    with urlopen(request, timeout=30, context=ssl_context) as response:
        payload = json.load(response)

    # API 成功時會回傳 RS: OK；失敗時停止並顯示回傳訊息。
    if payload.get("RS") != "OK":
        raise RuntimeError(f"API 回傳失敗：{payload}")

    # 只輸出實際交易資料陣列，不保留 RS 等 API 狀態資訊。
    records = payload.get("Data", [])
    with OUTPUT_PATH.open("w", encoding="utf-8") as output_file:
        json.dump(records, output_file, ensure_ascii=False, indent=2)
        output_file.write("\n")

    print(f"已抓取 {len(records)} 筆資料至：{OUTPUT_PATH}")


if __name__ == "__main__":
    main()
