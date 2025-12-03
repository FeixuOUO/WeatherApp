# wsgi.py

import os
import json
import requests
from flask import Flask, request, jsonify 
from http import HTTPStatus
from flask_cors import CORS 

app = Flask(__name__)
CORS(app) # 確保已啟用

# 從環境變數中讀取 API Key (API Key MUST be set in Vercel settings)
API_KEY = os.environ.get('OPENWEATHER_API_KEY')
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


# *** 最終修正：將路由從 '/api/weather' 改為 '/weather' ***
@app.route('/weather', methods=['GET', 'OPTIONS'])
def get_weather():
    """
    Flask 路由處理 /weather 請求
    """
    
    # 1. 獲取查詢參數
    city = request.args.get('city')

    if not city:
        return jsonify({'error': 'Missing city parameter'}), HTTPStatus.BAD_REQUEST

    if not API_KEY:
        # Vercel 上的 API Key 錯誤，回傳 500
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