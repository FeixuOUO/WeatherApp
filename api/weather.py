# api/weather.py (修改版)

import os
import json
import requests
from http import HTTPStatus

# 從環境變數中讀取 API Key，這是 Vercel 部署的標準做法
API_KEY = os.environ.get('OPENWEATHER_API_KEY')
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# 設置 CORS 標頭，重複定義是為了方便使用
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
    # 處理預檢請求 (OPTIONS request)
    # Vercel 的 request 物件可能沒有 .method 屬性，這裡使用字典的 .get() 增加容錯
    if request.get('method') == 'OPTIONS':
        return {
            'statusCode': HTTPStatus.OK,
            'headers': CORS_HEADERS,
            'body': ''
        }
        
    # 假設我們只接受 GET 請求
    if request.get('method') not in ['GET', None]: # 這裡也假設若無 method 屬性則為 GET 請求
        return {
            'statusCode': HTTPStatus.METHOD_NOT_ALLOWED,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Method not allowed'})
        }

    # 關鍵修改：從 request.query_string 或 request.args 中獲取參數
    # 由於 Vercel 的實際運行環境複雜，我們假設 'query' 屬性可能被包在 'args' 或 'params' 中
    # 這裡我們先嘗試使用 request.query (若它存在)
    query_params = request.get('query', {}) # 嘗試從 'query' 鍵獲取，否則使用空字典

    # 如果還是找不到 'city'，請注意：實際 Vercel 環境可能使用 'args' 或其他鍵
    city = query_params.get('city') 
    
    # 備用檢查：如果 city 仍然為 None，您可以嘗試從其他可能的參數鍵中尋找
    if not city:
        city = request.get('args', {}).get('city')


    if not city:
        return {
            'statusCode': HTTPStatus.BAD_REQUEST,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Missing city parameter'})
        }
    
    if not API_KEY:
        # 這裡的錯誤檢查是正確的，不需要改動
        return {
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'API Key not configured on the server'})
        }

    # 構建 OpenWeatherMap 的 API 請求 URL (與您原來的程式碼相同)
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric',  # 使用攝氏度
        'lang': 'zh_tw'      # 語言為繁體中文
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status() 

        return {
            'statusCode': HTTPStatus.OK,
            'headers': CORS_HEADERS,
            'body': response.text
        }

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        # 確保 e.response.json() 是可用的
        try:
             error_message = e.response.json().get('message', 'Unknown API Error')
        except json.JSONDecodeError:
             error_message = e.response.text # 如果回傳的不是 JSON，使用文字
             
        
        # 錯誤處理邏輯與您原來的程式碼相同
        if status_code == 404:
            return {
                'statusCode': HTTPStatus.NOT_FOUND,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': f'City not found: {city}'})
            }
            
        return {
            'statusCode': status_code,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': f'Weather API failed: {error_message}'})
        }
    except requests.exceptions.RequestException as e:
        return {
            'statusCode': HTTPStatus.SERVICE_UNAVAILABLE,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Failed to connect to weather service'})
        }