from __future__ import annotations

import os
from datetime import datetime

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# 说明：你给的 Key 直接写在这里了，方便你本地直接跑。
# 如果你后续想更安全一些，可以把它放到环境变量 WEATHERAPI_KEY。
DEFAULT_API_KEY = "60c6d521f8b543c4a3372318261507"


def get_api_key() -> str:
    return os.getenv("WEATHERAPI_KEY", DEFAULT_API_KEY).strip()


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/weather")
def api_weather():
    city = (request.args.get("city") or "").strip()
    if not city:
        return jsonify({"ok": False, "message": "请输入城市名，例如：北京、上海、深圳"}), 400

    api_key = get_api_key()
    url = "https://api.weatherapi.com/v1/forecast.json"

    try:
        resp = requests.get(
            url,
            params={
                "key": api_key,
                "q": city,
                "days": 8,  # today + future 7 days
                "aqi": "yes",  # 开启空气质量数据
                "alerts": "no",
                "lang": "zh",
            },
            timeout=10,
        )
    except requests.RequestException:
        return jsonify({"ok": False, "message": "网络请求失败，请检查你的网络后重试。"}), 502

    if resp.status_code != 200:
        try:
            err_msg = resp.json().get("error", {}).get("message")
        except Exception:
            err_msg = None

        return (
            jsonify(
                {
                    "ok": False,
                    "message": err_msg
                    or "没有找到该城市，请换个城市名试试（支持中文/英文）。",
                }
            ),
            404,
        )

    data = resp.json()

    location = data.get("location", {})
    current = data.get("current", {})
    forecast_days = (data.get("forecast", {}) or {}).get("forecastday", [])

    def safe_float(x, default=None):
        try:
            return float(x)
        except Exception:
            return default

    def safe_int(x, default=None):
        try:
            return int(x)
        except Exception:
            return default

    # 解析空气质量数据
    air_quality_raw = current.get("air_quality", {}) or {}
    air_quality = None
    if air_quality_raw:
        epa_index = safe_int(air_quality_raw.get("us-epa-index"))
        air_quality = {
            "pm2_5": safe_float(air_quality_raw.get("pm2_5")),
            "pm10": safe_float(air_quality_raw.get("pm10")),
            "o3": safe_float(air_quality_raw.get("o3")),
            "no2": safe_float(air_quality_raw.get("no2")),
            "so2": safe_float(air_quality_raw.get("so2")),
            "co": safe_float(air_quality_raw.get("co")),
            "us_epa_index": epa_index,  # 1-6
        }

    # 组装前端需要的最小数据
    result = {
        "ok": True,
        "city": location.get("name") or city,
        "country": location.get("country"),
        "region": location.get("region"),
        "localtime": location.get("localtime"),
        "current": {
            "temp_c": safe_float(current.get("temp_c")),
            "feelslike_c": safe_float(current.get("feelslike_c")),
            "humidity": current.get("humidity"),
            "wind_kph": safe_float(current.get("wind_kph")),
            "is_day": current.get("is_day"),
            "condition": {
                "text": (current.get("condition") or {}).get("text"),
                "icon": (current.get("condition") or {}).get("icon"),
                "code": (current.get("condition") or {}).get("code"),
            },
        },
        "air_quality": air_quality,
        "forecast": [],
        "hourly": [],  # 当天逐小时预报
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }

    # 逐日预报
    for d in forecast_days:
        day = d.get("day", {})
        result["forecast"].append(
            {
                "date": d.get("date"),
                "maxtemp_c": safe_float(day.get("maxtemp_c")),
                "mintemp_c": safe_float(day.get("mintemp_c")),
                "condition": {
                    "text": (day.get("condition") or {}).get("text"),
                    "icon": (day.get("condition") or {}).get("icon"),
                    "code": (day.get("condition") or {}).get("code"),
                },
            }
        )

    # 逐小时预报（取今天的 hour 数据）
    if forecast_days:
        hours = forecast_days[0].get("hour", []) or []
        for h in hours:
            result["hourly"].append(
                {
                    "time": h.get("time"),  # "2026-07-15 00:00"
                    "temp_c": safe_float(h.get("temp_c")),
                    "condition": {
                        "text": (h.get("condition") or {}).get("text"),
                        "icon": (h.get("condition") or {}).get("icon"),
                        "code": (h.get("condition") or {}).get("code"),
                    },
                    "wind_kph": safe_float(h.get("wind_kph")),
                    "humidity": safe_int(h.get("humidity")),
                    "chance_of_rain": safe_int(h.get("chance_of_rain")),
                }
            )

    return jsonify(result)


if __name__ == "__main__":
    # 便于本地开发：开启 debug，自动重载
    app.run(host="127.0.0.1", port=5000, debug=True)
