// script.js

// 注意：當您部署到 Vercel 後，您的後端函式路徑就是 /api/weather
// 部署後，這會指向您的 weather.py 檔案
const API_ENDPOINT = '/api/weather'; 

async function fetchWeather() {
    const cityInput = document.getElementById('city-input');
    const city = cityInput.value.trim();
    const resultDiv = document.getElementById('weather-result');
    const errorDiv = document.getElementById('error-message');
    
    resultDiv.innerHTML = '<p>正在查詢中...</p>';
    resultDiv.classList.remove('error');
    errorDiv.style.display = 'none';

    if (!city) {
        resultDiv.innerHTML = '<p>請輸入有效的城市名稱！</p>';
        return;
    }

    try {
        // 呼叫 Vercel 上的 Python 後端函式
        const response = await fetch(`${API_ENDPOINT}?city=${encodeURIComponent(city)}`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP 錯誤：${response.status}`);
        }

        const data = await response.json();
        
        // 解析並渲染數據
        renderWeather(data);

    } catch (error) {
        console.error('Fetch error:', error);
        resultDiv.innerHTML = ''; // 清空結果區
        errorDiv.textContent = `查詢失敗: ${error.message}`;
        errorDiv.style.display = 'block';
    }
}

function renderWeather(data) {
    const resultDiv = document.getElementById('weather-result');
    const temp = Math.round(data.main.temp); // 溫度取整數
    const description = data.weather[0].description;
    const iconCode = data.weather[0].icon;
    const humidity = data.main.humidity;
    const windSpeed = data.wind.speed;

    // OpenWeatherMap 的圖示連結
    const iconUrl = `https://openweathermap.org/img/wn/${iconCode}@2x.png`;

    resultDiv.innerHTML = `
        <h2>${data.name}, ${data.sys.country}</h2>
        <div class="weather-main">
            <img src="${iconUrl}" alt="${description}">
            <p class="temperature">${temp}°C</p>
        </div>
        <p class="description">天氣狀況: ${description}</p>
        <p>濕度: ${humidity}%</p>
        <p>風速: ${windSpeed} m/s</p>
    `;
}