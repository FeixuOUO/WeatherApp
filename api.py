# api.py

import os
import json
import requests
from flask import Flask, request, jsonify 
from http import HTTPStatus
from flask_cors import CORS # *** 修正 1: 導入 CORS 擴展 ***

# -------------------------------------------------------------
# *** 修正 2: 在 Vercel 環境下，不應導入 werkzeug.wrappers.Response
# Vercel 應用程式介面不需要這個，可能會造成衝突，因此移除。
# from werkzeug.wrappers import Response 
# -------------------------------------------------------------

app = Flask(__name__)
CORS(app) # *** 修正 3: 啟用 CORS for all routes ***

# 從環境變數中讀取 API Key 
API_KEY = os.environ.get('OPENWEATHER_API_KEY')
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


@app.route('/api/weather', methods=['GET', 'OPTIONS'])
def get_weather():
    """
    Flask 路由處理 /api/weather 請求
    """
    
    # 由於使用了 CORS(app)，Flask-CORS 會自動處理 OPTIONS 預檢請求
    # 這裡可以精簡 OPTIONS 處理邏輯 (僅為展示，保留以供參考)
    if request.method == 'OPTIONS':
        # Vercel 需要這些 CORS 標頭，Flask 路由級別處理
        # 這裡的回應將由 CORS(app) 自動添加必要的標頭
        return Response(status=HTTPStatus.NO_CONTENT) # 回應 204 No Content

    # 1. 獲取查詢參數 (Flask 的 request 物件更穩定)
    city = request.args.get('city')

    if not city:
        return jsonify({'error': 'Missing city parameter'}), HTTPStatus.BAD_REQUEST

    # *** 修正 4: 將 API Key 檢查移至此處，更安全 ***
    if not API_KEY:
        return jsonify({'error': 'API Key not configured on the server'}), HTTPStatus.INTERNAL_SERVER_ERROR

    # 2. 構建 OpenWeatherMap 的 API 請求 URL 
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric',  
        'lang': 'zh_tw'     
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()

        # 3. 返回 JSON 數據給前端
        response_data = response.json()
        
        # *** 修正 5: 由於使用了 CORS(app)，不再需要手動設置 response.headers['Access-Control-Allow-Origin']
        # 移除這行，讓 Flask-CORS 處理，更乾淨
        return jsonify(response_data)

    except requests.exceptions.HTTPError as e:
        # 錯誤處理 (簡化為 Flask 慣例)
        if e.response.status_code == 404:
            return jsonify({'error': f'City not found: {city}'}), HTTPStatus.NOT_FOUND
            
        try:
            error_message = e.response.json().get('message', 'Unknown API Error')
        except:
            error_message = e.response.text

        return jsonify({'error': f'Weather API failed: {error_message}'}), e.response.status_code
    
    except requests.exceptions.RequestException:
        return jsonify({'error': 'Failed to connect to weather service'}), HTTPStatus.SERVICE_UNAVAILABLE