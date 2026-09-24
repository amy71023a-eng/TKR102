import json
import ssl
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


START_TIME = "2026/07/01"  # 交易日期（起）
END_TIME = "2026/07/31"  # 交易日期（迄）
OUTPUT_FILE = Path("moa_2026_07_poultry_eggs.json")
API_URL = "https://data.moa.gov.tw/api/v1/PoultryTransType_BoiledChicken_Eggs/"

# 在 VS Code 中可用 FIELD_NAMES["egg_Price"] 查詢中文欄位名稱。
FIELD_NAMES = {
    "Start_time": "交易日期(起)",
    "End_time": "交易日期(迄)",
    "TransDate": "交易日期",
    "LunarCalendar": "農曆",
    "TaijinPrice_2.0kgup": "白肉雞2.0Kg以上(元/台斤)",
    "TaijinPrice_1.75kg_1.95kg": "白肉雞1.75-1.95Kg(元/台斤)",
    "Store_KP_TaijinPrice": "白肉雞門市價高屏(元/台斤)",
    "egg_Price": "雞蛋大運輸價(元/台斤)",
    "egg_Producer_Price": "雞蛋產地價(元/台斤)",
}

API_FIELDS = [field for field in FIELD_NAMES if field not in {"Start_time", "End_time"}]


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

    # 此 API 的憑證在部分 macOS Python 版本會出現相容性問題。
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
        for item in payload.get("Data", []):
            # 起迄日為查詢條件，可能不在原始單筆資料中，因此統一補入輸出。
            records.append({
                "Start_time": START_TIME,
                "End_time": END_TIME,
                **{field: item.get(field) for field in API_FIELDS},
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