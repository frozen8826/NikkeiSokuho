import asyncio
from urllib.parse import urlparse
from wsgiref import headers
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime


# fiscoの記事を探し出すためのRSSURL
RSS_URL_MARKET_NEWS = "https://jp.investing.com/rss/news_25.rss"

# 記事取得を記録するためのフラグ（本日すでに取得済みか）
last_fetched_date = None

# 格納用
checked_urls = set()    

# フィスコの日経レンジを取得する
async def fetch_fisco_nikkei_range_exp():
    d = feedparser.parse(RSS_URL_MARKET_NEWS)
    debug_count_fisco_articles = 0
    for entry in d.entries:
        url = entry["link"]
        # fiscoの記事かつ未チェックのURLの場合、中身を見に行く
        if "fisco" in entry["author"].lower() and url not in checked_urls:
            debug_count_fisco_articles+=1  # デバッグ用
            # 記事ページにアクセス
            response = requests.get(url, headers = {
                "Host": "jp.investing.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Te": "trailers",
                "Connection": "keep-alive",
            })
            if response.status_code == 200:
                # 確認済みURLに追加
                checked_urls.add(entry["link"])

                # HTML をパース
                soup = BeautifulSoup(response.text, "html.parser")

                # <div id="article"> 内の内容を取得
                article_div = soup.find("div", id="article")
                if article_div:
                    article_text = article_div.get_text(separator="\n", strip=True)

                    # 記事内に「[本日の想定レンジ]」が含まれるかチェック
                    if "[本日の想定レンジ]" in article_text:
                        print("✅ 記事に[本日の想定レンジ]が含まれています！")
                        print("記事の内容:")
                        print(article_text)

                        # 記事取得成功 → その日は以降の取得を行わないよう記録
                        last_fetched_date = datetime.now().date()
                        break  # 1件取得できたらループを抜ける
                    else:
                        print("⚠ 記事に[本日の想定レンジ]が含まれていません")
                else:
                    print("⚠ 記事の内容を取得できませんでした。")
            else:
                print(f"⚠ ページ取得に失敗しました（ステータスコード: {response.status_code}）")
                print("🔹 [HTTP リクエスト情報 ]")
                print(f"  - メソッド: {response.request.method}")
                print(f"  - URL: {response.request.url}")
                print(f"  - ヘッダー:")
                for key, value in response.request.headers.items():
                    print(f"    {key}: {value}")

                if response.request.body:
                    print(f"  - ボディ:")
                    print(response.request.body.decode('utf-8', 'ignore'))  # ボディがある場合に出力

                print("🔹 [HTTP レスポンス情報]")
                print(f"  - ステータスコード: {response.status_code}")
                print(f"  - ヘッダー:")
                for key, value in response.headers.items():
                    print(f"    {key}: {value}")

                print(f"  - ボディ:\n{response.text[:500]}...")
            print("-" * 80)  # 区切り線
    print(f"fiscoの日経予想レンジは検出されませんでした。\n検索記事数:{debug_count_fisco_articles}")


asyncio.run(fetch_fisco_nikkei_range_exp())