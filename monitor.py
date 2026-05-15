import requests
from bs4 import BeautifulSoup
import json
import os

# 從 GitHub Secrets 讀取網址
WEBHOOK_URL = os.getenv("GOOGLE_CHAT_WEBHOOK")
PTT_URL = "https://www.ptt.cc/bbs/Gamesale/index.html"

def monitor():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        # 爬取 PTT GameSale
        res = requests.get(PTT_URL, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        items = soup.find_all('div', class_='r-ent')
        
        matches = []
        for item in items:
            a_tag = item.find('div', class_='title').find('a')
            if not a_tag: continue
            
            title = a_tag.text
            link = "https://www.ptt.cc" + a_tag['href']
            upper_title = title.upper()
            
            # 1. 關鍵字必須有 PS5 PRO
            if "PS5 PRO" in upper_title:
                # 2. 排除 [徵]、已售出、暫定、SOUTU
                exclude_list = ["已售出", "售出", "SOUTU", "暫定", "[徵", "面交中", "交換"]
                if any(x in upper_title for x in exclude_list):
                    continue
                
                # 3. 必須是 [售 ] 分類
                if "[售" in upper_title:
                    matches.append(f"🔥 發現 PS5 Pro 出售！\n標題：{title}\n連結：{link}")

        if matches:
            for msg in matches:
                send_notification(msg)
                print(f"發送成功: {msg}")
        else:
            print("目前沒發現符合條件的 PS5 Pro。")
                
    except Exception as e:
        print(f"錯誤: {e}")

def send_notification(text):
    payload = {"text": text}
    # 傳送到你的 GAS 網址
    requests.post(WEBHOOK_URL, data=json.dumps(payload), headers={'Content-Type': 'application/json'})

if __name__ == "__main__":
    monitor()