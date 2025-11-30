# api/weather.py (Version 3)

import os
import json
import requests
from http import HTTPStatus

# 這裡不再定義 API_KEY 或 BASE_URL
# ... 保持其他 import 內容不變

# 設置 CORS 標頭，移到頂層以簡化
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json',
}

def handler(request):
    """
    Vercel Serverless Function 的入口點。
    """
    # 【新增】將常數移到函式內部，確保它們在正確的執行環境中被定義
    API_KEY = os.environ.get('OPENWEATHER_API_KEY')
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    # ... (後續的 headers 和 OPTIONS 處理保持不變)

    # 處理預檢請求 (OPTIONS request)
    # ... (保持不變)
    
    # ... (獲取 city 參數邏輯保持不變)

    # ... (API Key 檢查邏輯保持不變)
    
    # ... (構建 API 請求及 try/except 區塊保持不變)
    
    # ...