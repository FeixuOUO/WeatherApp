# api/weather.py

import os
import json
import requests
from http import HTTPStatus

# 從環境變數中讀取 API Key，這是 Vercel 部署的標準做法
# 請在 Vercel 專案設定中添加 OPENWEATHER_API_KEY
API_KEY = os.environ.get('OPENWEATHER_API_KEY')
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def handler(request):
    """
    Vercel Serverless Function 的入口點。
    從前端獲取 'city' 參數，並向 OpenWeatherMap API 發出請求。
    """
    
    # 設置 HTTP 標頭，允許跨域請求 (CORS)
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*', # 允許所有網域存取
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    
    # 處理預檢請求 (OPTIONS request)
    if request.method == 'OPTIONS':
        return {
            'statusCode': HTTPStatus.OK,
            'headers': headers,
            'body': ''
        }
        
    if request.method != 'GET':
        return {
            'statusCode': HTTPStatus.METHOD_NOT_ALLOWED,
            'headers': headers,
            'body': json.dumps({'error': 'Method not allowed'})
        }

    # 獲取 URL 查詢參數
    query_params = request.query
    city = query_params.get('city')

    if not city:
        return {
            'statusCode': HTTPStatus.BAD_REQUEST,
            'headers': headers,
            'body': json.dumps({'error': 'Missing city parameter'})
        }

    if not API_KEY:
        return {
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR,
            'headers': headers,
            'body': json.dumps({'error': 'API Key not configured on the server'})
        }

    # 構建 OpenWeatherMap 的 API 請求 URL
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric',  # 使用攝氏度
        'lang': 'zh_tw'      # 語言為繁體中文
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # 如果狀態碼是 4xx 或 5xx，則拋出異常

        # 將氣象 API 的回應直接傳回給前端
        return {
            'statusCode': HTTPStatus.OK,
            'headers': headers,
            'body': response.text
        }

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        error_message = e.response.json().get('message', 'Unknown API Error')
        
        # 特別處理找不到城市的情況 (404)
        if status_code == 404:
            return {
                'statusCode': HTTPStatus.NOT_FOUND,
                'headers': headers,
                'body': json.dumps({'error': f'City not found: {city}'})
            }
            
        return {
            'statusCode': status_code,
            'headers': headers,
            'body': json.dumps({'error': f'Weather API failed: {error_message}'})
        }
    except requests.exceptions.RequestException as e:
        return {
            'statusCode': HTTPStatus.SERVICE_UNAVAILABLE,
            'headers': headers,
            'body': json.dumps({'error': 'Failed to connect to weather service'})
        }