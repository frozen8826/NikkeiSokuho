from pyppeteer import launch
import asyncio
import json
import os
import re
from datetime import datetime, timezone, timedelta

# 日本時間の設定
JST = timezone(timedelta(hours=9))

# クローリング対象
URL = "https://jp.investing.com/news/stock-market-news/article-1015305"

# JSONデータ保存先
DATA_FILE = "data.json"

# -----------関数定義---------------
def load_data():
    # JSONファイルから過去のチェック履歴を読み込む
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {"date": "", "found": False, "checked_urls": []}

def save_data(data):
    # チェック履歴をJSONファイルに保存
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

async def main(data):
    browser = await launch(
        headless=False,
        executablePath="C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
        args=['--no-sandbox']  # 一部の環境では --no-sandbox が必要
    )
    page = await browser.newPage()
    await page.goto(URL, {'waitUntil': 'domcontentloaded'})
    
    # 記事のタイトルを取得
    title = await page.title()

    # チェック済みURLとして記録
    data["checked_urls"].append(URL)

    # 記事の本文を取得
    content = await page.evaluate('''
            () => {
                let article = document.querySelector("#article");
                return article ? article.innerText : "";
            }
        ''')

    # 記事の中に [予想レンジ] または [本日の想定レンジ] があるか探す
    if any(keyword in content for keyword in ["[予想レンジ]", "[本日の想定レンジ]"]):
        # 不要な広告文を削除
        content = re.sub(
            r"第三者による広告。Investing\.comの提案や推奨ではありません。こちらで開示情報をご覧いただくか、広告を削除してください。",
            "",
            content
        )
        print(f"記事内容:\n{content}")
        data["date"] = datetime.now(JST).strftime("%Y-%m-%d")
        data["found"] = True
        print("data",data)
    else:
        print("ヒットなし")

    await browser.close()
    save_data(data)

# -----------main---------------
# jsonデータ受け取り
data = load_data()

today_str = datetime.now(JST).strftime("%Y-%m-%d")
print("today_str",today_str)
if data["date"] != today_str:  
    # 日付が違う場合、リセット
    data = {"date": today_str, "found": False, "checked_urls": []}

# 見つかっていない場合に走査
if not data["found"] and URL not in data["checked_urls"]:
    asyncio.run(main(data))
else:
    print(f"本日は既に走査済みか、チェック済みURLです。(found:{data['found']}, checked?:{URL not in data['checked_urls']})")

