import asyncio
import json
import os
import discord
from discord.ext import commands
from datetime import datetime, timezone, timedelta
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pyppeteer import launch
import asyncio
import re
import subprocess
from database import SessionLocal
import crud
from pydantic import BaseModel
from main import get_db
import os
from dotenv import load_dotenv
 
load_dotenv()

# 日本時間の設定
JST = timezone(timedelta(hours=9))

# クローリング対象のURL
RSS_URL = "https://jp.investing.com/rss/news_25.rss"

# Chrome実行ファイルの場所
CHROME_PATH = os.getenv("CHROME_PATH")

# JSONデータ保存先
DATA_FILE = "data.json"

# Discord BotのID
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# チェック時刻
db = next(get_db())  
CHECK_TIMES = [item.scan_time for item in crud.get_scan_time(db) if item.bot_id == 1]

#--------------------------関数定義-----------------------------
def load_data():
    """JSONファイルから設定を読み込む"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {"date": "", "found": False, "checked_urls": [], "channel_id": None}

def save_data(data):
    """ 設定をJSONファイルに保存 """
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

# データをロード
data = load_data()

# 日付が違う場合、リセット
today_str = datetime.now(JST).strftime("%Y-%m-%d")
if data["date"] != today_str: 
    data = {"date": today_str, "found": False, "checked_urls": []}

#--------------------------Discord Bot クラス-----------------------------
class MyClient(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    async def setup_hook(self):
        """ Bot起動時にスケジュールタスクを設定 """
        self.check_rss_at_times()

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    @staticmethod
    async def get_channels(client):
        """ Botが参加しているサーバーのテキストチャンネルを取得 """
        for guild in client.guilds:
            for channel in guild.text_channels:
                yield channel 

    @staticmethod
    async def send_message(client, text):
        """ 最初に見つかった発言可能なチャンネルにメッセージを送信 """
        async for channel in MyClient.get_channels(client):
            await channel.send(text)
            break

    async def notice_nikkei_range_forecast(self):
        now = datetime.now(JST).strftime("%H:%M")
        print(f"{now}：記事スクレイピングを開始します")
        """ RSSをチェックし、予想レンジの記事があれば通知する """
        d = feedparser.parse(RSS_URL)
        debug_count_fisco_articles = 0
        
        for entry in d.entries:
            # 既に確認済みであれば実行しない
            if data["found"] is True:
                break

            url = entry["link"]
            # fiscoの記事かつ未チェックのURLの場合、中身を見に行く
            if "fisco" in entry["author"].lower() and url not in data["checked_urls"]:
                debug_count_fisco_articles+=1  # デバッグ用
                # 確認済みURLに追加
                data["checked_urls"].append(entry.link) 
                # ブラウザ準備
                browser = await launch(
                    headless=False,  
                    executablePath=CHROME_PATH,
                    args=['--no-sandbox'] 
                )
                page = await browser.newPage()
                # 記事ページにアクセス
                await page.goto(url, {'waitUntil': 'domcontentloaded'})
    
                # 記事の本文を取得
                content = await page.evaluate('''
                    () => {
                        let article = document.querySelector("#article");
                        return article ? article.innerText : "";
                    }
                ''')

                # 記事内に「[本日の想定レンジ]」が含まれるかチェック
                if "[本日の想定レンジ]" in content:
                    title = await page.title()
                    content = re.sub(r"第三者による広告。Investing\.comの提案や推奨ではありません。こちらで開示情報をご覧いただくか、広告を削除してください。", "", content)

                    print("記事に[本日の想定レンジ]が含まれています！")
                    print("記事の内容:")
                    print(content)
                    await MyClient.send_message(self, content)
                    # 記事取得成功 → その日は以降の取得を行わないよう記録
                    data["date"] = datetime.now(JST).strftime("%Y-%m-%d")
                    data["found"] = True
                    save_data(data)
                    await browser.close()
                    break  # 1件取得できたらループを抜ける
                await browser.close()
            await asyncio.sleep(10) # アクセス頻度を控えるため10秒スリープ
        print(f"fiscoの日経予想レンジは検出されませんでした。\n検索記事数(fisco):{debug_count_fisco_articles}")
        
    def check_rss_at_times(self):
        """ 固定された時刻でRSSをチェックする """
        for time_str in CHECK_TIMES:
            print(f"タスクを作成：{time_str}")
            asyncio.create_task(self.check_rss_at_time(time_str))

    async def check_rss_at_time(self, time_str):
        """ 指定された時刻にRSSチェックを実行 """
        while True:
            now = datetime.now(JST).strftime("%H:%M")
            if now == time_str:
                await self.notice_nikkei_range_forecast()
            await asyncio.sleep(60)  # 1分ごとにチェック
    
     

#--------------------------main-----------------------------
# discordのbot立ち上げ
intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(DISCORD_BOT_TOKEN)

