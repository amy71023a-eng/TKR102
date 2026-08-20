import time
import requests
from bs4 import BeautifulSoup


def get_recipe_data(seq: str) -> dict:
    """傳入食譜的 seq 代碼，爬取並回傳該食譜的詳細資料

    :param seq: 食譜編號 (例如: 'C01-0219')
    :return: 包含食譜各項資料的字典 (dict)
    """
    url = f"https://www.ytower.com.tw/recipe/iframe-recipe.asp?seq={seq}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        # 自動處理 UTF-8 / BIG5 等網頁編碼問題
        response.encoding = response.apparent_encoding

        if response.status_code != 200:
            print(f"無法存取頁面 [{seq}]，HTTP 狀態碼: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # 1. 食譜名稱
        recipe_name_tag = soup.select_one("div#recipe_name h2 a")
        recipe_name = (
            recipe_name_tag.text.strip() if recipe_name_tag else "未知食譜名稱"
        )

        # 2. 材料
        ingredients = [
            item.text.strip() for item in soup.select("span.ingredient_name")
        ]

        # 3. 作法步驟
        steps = [
            item.text.strip().replace("\r", "").replace("\n", "")
            for item in soup.select("li.step")
        ]

        # 4. 關鍵字 / 標籤
        keywords = [
            a.text.strip()
            for a in soup.select("div.recie_tag a")
            if a.text.strip()
        ]

        # 5. 上線時間
        time_tag = soup.select_one("time")
        if time_tag:
            # 優先取得 <time datetime="..."> 屬性值，若無則取得標籤內的文字
            upload_date = time_tag.get("datetime") or time_tag.text.strip()
        else:
            upload_date = "未找到上線時間"

        return {
            "seq": seq,
            "url": url,
            "食譜名稱": recipe_name,
            "上線時間": upload_date,
            "關鍵字": keywords,
            "材料": ingredients,
            "作法步驟": steps,
        }

    except Exception as e:
        print(f"爬取 [{seq}] 時發生錯誤: {e}")
        return None


# ==================== 執行範例 ====================
if __name__ == "__main__":
    # 指定要爬取的料理 seq 代碼：
    # C01-0219: 脆皮雞蛋糕
    # C01-0325: 海綿蛋糕
    target_recipes = ["C01-0219", "C01-0325"]

    all_recipes = []

    for seq in target_recipes:
        print(f"正在爬取 seq={seq} ...")
        data = get_recipe_data(seq)

        if data:
            all_recipes.append(data)

            # 印出排版後的結果
            print("=" * 50)
            print(f"【食譜名稱】: {data['食譜名稱']}")
            print(f"【上線時間】: {data['上線時間']}")
            print(f"【關鍵字】  : {', '.join(data['關鍵字'])}")
            print("\n【材料】:")
            for ing in data["材料"]:
                print(f"  - {ing}")

            print("\n【作法步驟】:")
            for idx, step in enumerate(data["作法步驟"], 1):
                print(f"  {step}")
            print("=" * 50 + "\n")

        # 禮貌爬蟲：每次請求間隔 1 秒，保護目標伺服器
        time.sleep(1)