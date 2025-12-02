# api.py (Flask 版本)

import os
import json
import requests
from flask import Flask, request, jsonify # 導入 Flask 相關模組
from http import HTTPStatus
from werkzeug.wrappers import Response # 用於 Vercel Serverless 包裝

app = Flask(__name__)

# 從環境變數中讀取 API Key (這裡仍然是函式外部，但 Flask 會正確處理)
API_KEY = os.environ.get('OPENWEATHER_API_KEY')
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


@app.route('/api/weather', methods=['GET', 'OPTIONS'])
def get_weather():
    """
    Flask 路由處理 /api/weather 請求
    """
    
    # 處理 OPTIONS 預檢請求
    if request.method == 'OPTIONS':
        # Vercel 需要這些 CORS 標頭，Flask 路由級別處理
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    # 1. 獲取查詢參數 (Flask 的 request 物件更穩定)
    city = request.args.get('city')

    if not city:
        return jsonify({'error': 'Missing city parameter'}), HTTPStatus.BAD_REQUEST

    if not API_KEY:
        return jsonify({'error': 'API Key not configured on the server'}), HTTPStatus.INTERNAL_SERVER_ERROR

    # 2. 構建 OpenWeatherMap 的 API 請求 URL (與之前相同)
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
        # jsonify 自動設定 Content-Type: application/json
        # 並確保 CORS 標頭在回應中
        response_data = response.json()
        flask_response = jsonify(response_data)
        flask_response.headers['Access-Control-Allow-Origin'] = '*'
        return flask_response

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

# Vercel 需要一個單獨的 wsgi 入口點，通常是 app 變數本身
# 實際部署時，Vercel 會自動找到這個 app 變數並執行