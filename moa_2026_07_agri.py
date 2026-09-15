import json
import ssl
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


START_TIME = "115.07.01"  # 交易日期（起）
END_TIME = "115.07.30"  # 交易日期（迄）
OUTPUT_FILE = Path("moa_2026_07_agri_filtered.json")
API_URL = "https://data.moa.gov.tw/api/v1/AgriProductsTransType/"

# 在 VS Code 中可用 FIELD_NAMES["CropName"] 查詢中文欄位名稱。
FIELD_NAMES = {
    "Start_time": "交易日期(起)",
    "End_time": "交易日期(迄)",
    "CropCode": "農產品代碼",
    "CropName": "農產品名稱",
    "Avg_Price": "平均價(元/公斤)",
}


def fetch_page(page: int | None = None) -> dict:
    """取得一頁 API 資料。"""
    params = {"Start_time": START_TIME, "End_time": END_TIME}
    if page is not None:
        params["Page"] = str(page)

    request = Request(
        f"{API_URL}?{urlencode(params)}",
        headers={"Accept": "application/json"},
        method="GET",
    )

    # 此端點的憑證在部分 macOS Python 版本無法通過驗證。
    context = ssl._create_unverified_context()
    try:
        with urlopen(request, timeout=30, context=context) as response:
            return json.load(response)
    except HTTPError as error:
        raise SystemExit(f"API request failed: HTTP {error.code} {error.reason}")
    except URLError as error:
        raise SystemExit(f"Unable to reach the API: {error.reason}")
    except json.JSONDecodeError:
        raise SystemExit("The API response was not valid JSON.")


def main() -> None:
    records = []
    page = None

    # API 每頁最多回傳 1,000 筆。只要 Next 為 true，就讀取下一頁。
    while True:
        payload = fetch_page(page)
        for item in payload.get("Data", []):
            # Start_time、End_time 是查詢條件，不會出現在 API 的每筆回傳資料，
            # 因此在輸出時補入，讓每筆資料都有五個指定欄位。
            records.append({
                "Start_time": START_TIME,
                "End_time": END_TIME,
                "CropCode": item.get("CropCode"),
                "CropName": item.get("CropName"),
                "Avg_Price": item.get("Avg_Price"),
            })

        if not payload.get("Next", False):
            break
        page = 2 if page is None else page + 1

    OUTPUT_FILE.write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Saved {len(records)} records to: {OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()