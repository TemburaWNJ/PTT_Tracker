import requests
from bs4 import BeautifulSoup
import json
import os
import time

WEBHOOK_URL = os.getenv("GOOGLE_CHAT_WEBHOOK")
PTT_URL = "https://www.ptt.cc/bbs/Gamesale/index.html"

def monitor():
    # 建立一個 Session 物件，這會自動處理 Cookie（例如 18 歲確認）
    session = requests.Session()
    
    # 模擬更真實的瀏覽器 Headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
    }
    
    try:
        # 1. 先進首頁設定 over18 的 Cookie (PTT 買賣版通常需要)
        session.post("https://www.ptt.cc/ask/over18", data={'yes': 'yes'}, headers=headers)
        
        # 2. 正式爬取頁面
        res = session.get(PTT_URL, headers=headers, timeout=15)
        
        # 如果還是被擋（狀態碼不是 200），報錯
        if res.status_code != 200:
            print(f"存取失敗，狀態碼：{res.status_code}")
            return

        soup = BeautifulSoup(res.text, 'html.parser')
        items = soup.find_all('div', class_='r-ent')
        
        print(f"--- 成功連線 PTT，開始掃描 {len(items)} 篇文章 ---")
        matches = []
        
        for item in items:
            title_div = item.find('div', class_='title')
            a_tag = title_div.find('a')
            if not a_tag: continue
            
            title = a_tag.text
            link = "https://www.ptt.cc" + a_tag['href']
            upper_title = title.upper()
            
            if "PS5 PRO" in upper_title:
                exclude_list = ["已售出", "售出", "SOUTU", "暫定", "[徵", "面交中", "交換"]
                if any(x in upper_title for x in exclude_list):
                    continue
                
                if "[售" in upper_title:
                    matches.append(f"🔥 發現 PS5 Pro 出售！\n標題：{title}\n連結：{link}")

        if matches:
            for msg in matches:
                send_notification(msg)
        else:
            print("--- 本次掃描完畢，無符合條件資料 ---")
                
    except Exception as e:
        print(f"發生錯誤: {e}")

def send_notification(text):
    payload = {"text": text}
    try:
        requests.post(WEBHOOK_URL, data=json.dumps(payload), headers={'Content-Type': 'application/json'}, timeout=10)
        print("通知發送成功")
    except Exception as e:
        print(f"發送通知失敗: {e}")

if __name__ == "__main__":
    monitor()
