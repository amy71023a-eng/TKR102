import json
import ssl
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


START_TIME = "1150701"  # 查詢起日：民國年月日
END_TIME = "1150731"  # 查詢迄日：民國年月日
OUTPUT_FILE = Path("moa_2026_07_fishery.json")
API_URL = "https://data.moa.gov.tw/api/v1/FisheryProductsTransType/"

# 在 VS Code 中可用 FIELD_NAMES["Avg_Price"] 查詢中文欄位名稱。
FIELD_NAMES = {
    "SeafoodProdCode": "漁產品代碼",
    "SeafoodProdName": "漁產品名稱(含各語系)",
    "MarketName": "市場名稱(含各語系)",
    "TransDate": "交易日期(民國年，例如107-05-01)",
    "Upper_Price": "上價(元/公斤)",
    "Middle_Price": "中價(元/公斤)",
    "Lower_Price": "下價(元/公斤)",
    "Trans_Quantity": "交易量(公斤)",
    "Avg_Price": "平均價(元/公斤)",
}

SELECTED_FIELDS = list(FIELD_NAMES)


def fetch_page(page: int | None = None) -> dict:
    """取得 API 的一頁資料。"""
    params = {"Start_time": START_TIME, "End_time": END_TIME}
    if page is not None:
        params["Page"] = str(page)

    request = Request(
        f"{API_URL}?{urlencode(params)}",
        headers={"Accept": "application/json"},
        method="GET",
    )

    # 部分 macOS Python 會拒絕此 API 的憑證；此設定僅限本 API 使用。
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

    # API 若回傳 Next=true，代表仍有下一頁資料。
    while True:
        payload = fetch_page(page)
        records.extend(
            {field: item.get(field) for field in SELECTED_FIELDS}
            for item in payload.get("Data", [])
        )

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