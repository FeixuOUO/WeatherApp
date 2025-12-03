# wsgi.py

import os
import json
import requests
from flask import Flask, request, jsonify 
from http import HTTPStatus
from flask_cors import CORS 

app = Flask(__name__)
CORS(app) # 啟用 CORS for all routes

# 從環境變數中讀取 API Key (API Key MUST be set in Vercel settings)
API_KEY = os.environ.get('OPENWEATHER_API_KEY')
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


@app.route('/api/weather', methods=['GET', 'OPTIONS'])
def get_weather():
    """
    Flask 路由處理 /api/weather 請求
    """
    
    # 由於使用了 CORS(app)，Flask-CORS 會自動處理 OPTIONS 預檢請求，
    # 這裡的邏輯只處理 GET 請求和錯誤。

    # 1. 獲取查詢參數 (Flask 的 request.args.get() 更穩定)
    city = request.args.get('city')

    if not city:
        return jsonify({'error': 'Missing city parameter'}), HTTPStatus.BAD_REQUEST

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
        
        # jsonify 自動添加 CORS 標頭
        return jsonify(response_data)

    except requests.exceptions.HTTPError as e:
        # 錯誤處理
        if e.response.status_code == 404:
            return jsonify({'error': f'City not found: {city}'}), HTTPStatus.NOT_FOUND
            
        try:
            error_message = e.response.json().get('message', 'Unknown API Error')
        except:
            error_message = e.response.text

        return jsonify({'error': f'Weather API failed: {error_message}'}), e.response.status_code
    
    except requests.exceptions.RequestException:
        return jsonify({'error': 'Failed to connect to weather service'}), HTTPStatus.SERVICE_UNAVAILABLE