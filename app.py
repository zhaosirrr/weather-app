from __future__ import annotations

import os
from datetime import datetime

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# 说明：你给的 Key 直接写在这里了，方便你本地直接跑。
# 如果你后续想更安全一些，可以把它放到环境变量 WEATHERAPI_KEY。
DEFAULT_API_KEY = "60c6d521f8b543c4a3372318261507"

CITY_NAME_MAP = {
    "北京": "Beijing",
    "上海": "Shanghai",
    "广州": "Guangzhou",
    "深圳": "Shenzhen",
    "杭州": "Hangzhou",
    "成都": "Chengdu",
    "南京": "Nanjing",
    "武汉": "Wuhan",
    "西安": "Xian",
    "重庆": "Chongqing",
    "天津": "Tianjin",
    "苏州": "Suzhou",
    "长沙": "Changsha",
    "郑州": "Zhengzhou",
    "青岛": "Qingdao",
    "厦门": "Xiamen",
    "大连": "Dalian",
    "沈阳": "Shenyang",
    "哈尔滨": "Harbin",
    "福州": "Fuzhou",
    "南宁": "Nanning",
    "昆明": "Kunming",
    "贵阳": "Guiyang",
    "兰州": "Lanzhou",
    "银川": "Yinchuan",
    "西宁": "Xining",
    "乌鲁木齐": "Urumqi",
    "呼和浩特": "Hohhot",
    "拉萨": "Lhasa",
    "海口": "Haikou",
    "珠海": "Zhuhai",
    "东莞": "Dongguan",
    "佛山": "Foshan",
    "中山": "Zhongshan",
    "惠州": "Huizhou",
    "宁波": "Ningbo",
    "无锡": "Wuxi",
    "常州": "Changzhou",
    "南通": "Nantong",
    "徐州": "Xuzhou",
    "温州": "Wenzhou",
    "绍兴": "Shaoxing",
    "嘉兴": "Jiaxing",
    "湖州": "Huzhou",
    "台州": "Taizhou",
    "金华": "Jinhua",
    "衢州": "Quzhou",
    "丽水": "Lishui",
    "舟山": "Zhoushan",
    "石家庄": "Shijiazhuang",
    "太原": "Taiyuan",
    "呼和浩特": "Hohhot",
    "沈阳": "Shenyang",
    "长春": "Changchun",
    "哈尔滨": "Harbin",
    "南京": "Nanjing",
    "杭州": "Hangzhou",
    "合肥": "Hefei",
    "福州": "Fuzhou",
    "南昌": "Nanchang",
    "济南": "Jinan",
    "郑州": "Zhengzhou",
    "武汉": "Wuhan",
    "长沙": "Changsha",
    "广州": "Guangzhou",
    "南宁": "Nanning",
    "海口": "Haikou",
    "重庆": "Chongqing",
    "成都": "Chengdu",
    "贵阳": "Guiyang",
    "昆明": "Kunming",
    "拉萨": "Lhasa",
    "西安": "Xian",
    "兰州": "Lanzhou",
    "西宁": "Xining",
    "银川": "Yinchuan",
    "乌鲁木齐": "Urumqi",
}

ENGLISH_TO_CHINESE_MAP = {
    "Beijing": "北京市",
    "Shanghai": "上海市",
    "Guangzhou": "广州市",
    "Shenzhen": "深圳市",
    "Hangzhou": "杭州市",
    "Chengdu": "成都市",
    "Nanjing": "南京市",
    "Wuhan": "武汉市",
    "Xian": "西安市",
    "Chongqing": "重庆市",
    "Tianjin": "天津市",
    "Suzhou": "苏州市",
    "Changsha": "长沙市",
    "Zhengzhou": "郑州市",
    "Qingdao": "青岛市",
    "Xiamen": "厦门市",
    "Dalian": "大连市",
    "Shenyang": "沈阳市",
    "Harbin": "哈尔滨市",
    "Fuzhou": "福州市",
    "Nanning": "南宁市",
    "Kunming": "昆明市",
    "Guiyang": "贵阳市",
    "Lanzhou": "兰州市",
    "Yinchuan": "银川市",
    "Xining": "西宁市",
    "Urumqi": "乌鲁木齐市",
    "Hohhot": "呼和浩特市",
    "Lhasa": "拉萨市",
    "Haikou": "海口市",
    "Zhuhai": "珠海市",
    "Dongguan": "东莞市",
    "Foshan": "佛山市",
    "Zhongshan": "中山市",
    "Huizhou": "惠州市",
    "Ningbo": "宁波市",
    "Wuxi": "无锡市",
    "Changzhou": "常州市",
    "Nantong": "南通市",
    "Xuzhou": "徐州市",
    "Wenzhou": "温州市",
    "Shaoxing": "绍兴市",
    "Jiaxing": "嘉兴市",
    "Huzhou": "湖州市",
    "Taizhou": "台州市",
    "Jinhua": "金华市",
    "Quzhou": "衢州市",
    "Lishui": "丽水市",
    "Zhoushan": "舟山市",
    "Shijiazhuang": "石家庄市",
    "Taiyuan": "太原市",
    "Changchun": "长春市",
    "Hefei": "合肥市",
    "Nanchang": "南昌市",
    "Jinan": "济南市",
    "Shanghaishih": "上海市",
}

AREA_TO_CITY_MAP = {
    "Meilong": "上海市",
    "Pudong": "上海市",
    "Xuhui": "上海市",
    "Jing'an": "上海市",
    "Changning": "上海市",
    "Hongkou": "上海市",
    "Yangpu": "上海市",
    "Huangpu": "上海市",
    "Putuo": "上海市",
    "Baoshan": "上海市",
    "Minhang": "上海市",
    "Jiading": "上海市",
    "Qingpu": "上海市",
    "Songjiang": "上海市",
    "Jinshan": "上海市",
    "Fengxian": "上海市",
    "Chongming": "上海市",
    "Beijing Shi": "北京市",
    "Dongcheng": "北京市",
    "Xicheng": "北京市",
    "Chaoyang": "北京市",
    "Haidian": "北京市",
    "Fengtai": "北京市",
    "Shijingshan": "北京市",
    "Mentougou": "北京市",
    "Fangshan": "北京市",
    "Tongzhou": "北京市",
    "Shunyi": "北京市",
    "Changping": "北京市",
    "Daxing": "北京市",
    "Huairou": "北京市",
    "Pinggu": "北京市",
    "Miyun": "北京市",
    "Yanqing": "北京市",
}


def get_api_key() -> str:
    return os.getenv("WEATHERAPI_KEY", DEFAULT_API_KEY).strip()


def translate_city_name(city: str) -> str:
    return CITY_NAME_MAP.get(city, city)


def get_chinese_city_name(city: str) -> str:
    if not city:
        return city
    
    city_upper = city.strip()
    
    if city_upper in ENGLISH_TO_CHINESE_MAP:
        return ENGLISH_TO_CHINESE_MAP[city_upper]
    
    if city_upper in AREA_TO_CITY_MAP:
        return AREA_TO_CITY_MAP[city_upper]
    
    city_base = city_upper.split()[0]
    if city_base in ENGLISH_TO_CHINESE_MAP:
        return ENGLISH_TO_CHINESE_MAP[city_base]
    
    if city_base in AREA_TO_CITY_MAP:
        return AREA_TO_CITY_MAP[city_base]
    
    for area, chinese_city in AREA_TO_CITY_MAP.items():
        if area.lower() in city_upper.lower():
            return chinese_city
    
    for eng, chinese_city in ENGLISH_TO_CHINESE_MAP.items():
        if eng.lower() in city_upper.lower():
            return chinese_city
    
    return city


@app.get("/")
def index():
    return render_template("index.html")


def get_public_ip():
    ip_services = [
        "https://api.ipify.org",
        "https://icanhazip.com",
        "https://ifconfig.me/ip",
    ]
    for url in ip_services:
        try:
            resp = requests.get(url, timeout=3)
            if resp.status_code == 200:
                ip = resp.text.strip()
                if ip and ip != "127.0.0.1":
                    return ip
        except requests.RequestException:
            continue
    return None


def get_city_by_ip(ip):
    try:
        resp = requests.get(
            "http://ip-api.com/json/",
            params={
                "query": ip,
                "fields": "city,country,lat,lon",
                "lang": "zh-CN",
            },
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            city = data.get("city")
            if city:
                return {
                    "city": city,
                    "country": data.get("country"),
                    "lat": data.get("lat"),
                    "lon": data.get("lon"),
                }
    except requests.RequestException:
        pass
    return None


def get_city_by_ip2(ip):
    try:
        resp = requests.get(
            f"https://ipinfo.io/{ip}/json",
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            city = data.get("city")
            if city:
                return {
                    "city": city,
                    "country": data.get("country"),
                    "lat": data.get("loc", "").split(",")[0] if data.get("loc") else None,
                    "lon": data.get("loc", "").split(",")[1] if data.get("loc") else None,
                }
    except requests.RequestException:
        pass
    return None


def get_city_by_ip3(ip):
    try:
        resp = requests.get(
            "https://api.sypexgeo.net/json/",
            params={"ip": ip},
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            city = data.get("city", {}).get("name_zh") or data.get("city", {}).get("name_en")
            if city:
                return {
                    "city": city,
                    "country": data.get("country", {}).get("name_zh"),
                    "lat": data.get("city", {}).get("lat"),
                    "lon": data.get("city", {}).get("lon"),
                }
    except requests.RequestException:
        pass
    return None


def get_city_by_ip4(ip):
    try:
        resp = requests.get(
            "https://api.ip.sb/geoip/" + ip,
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            city = data.get("city")
            if city:
                return {
                    "city": city,
                    "country": data.get("country"),
                    "lat": data.get("latitude"),
                    "lon": data.get("longitude"),
                }
    except requests.RequestException:
        pass
    return None


def get_city_by_ip5(ip):
    try:
        resp = requests.get(
            "https://freegeoip.app/json/" + ip,
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            city = data.get("city_name") or data.get("city")
            if city:
                return {
                    "city": city,
                    "country": data.get("country_name"),
                    "lat": data.get("latitude"),
                    "lon": data.get("longitude"),
                }
    except requests.RequestException:
        pass
    return None


def resolve_city_from_ip(ip):
    ip_resolvers = [get_city_by_ip, get_city_by_ip2, get_city_by_ip3, get_city_by_ip4, get_city_by_ip5]
    for resolver in ip_resolvers:
        result = resolver(ip)
        if result:
            return result
    return None


def get_default_city():
    import random
    test_cities = ["北京", "上海", "广州", "深圳", "杭州", "成都"]
    return random.choice(test_cities)


def get_city_name(city):
    if isinstance(city, str):
        return city
    return city.get("city") if isinstance(city, dict) else None


def get_city_name_in_chinese(city):
    city_name = get_city_name(city)
    if city_name:
        return translate_city_name(city_name)
    return None


@app.get("/api/location")
def api_location():
    client_ip = request.remote_addr
    
    if client_ip in ("127.0.0.1", "localhost", "::1"):
        public_ip = get_public_ip()
        if public_ip:
            city_info = resolve_city_from_ip(public_ip)
            if city_info:
                city_name = get_city_name(city_info)
                translated_name = translate_city_name(city_name) if city_name else None
                return jsonify({
                    "ok": True,
                    "city": translated_name or city_name,
                    "country": city_info.get("country"),
                    "lat": city_info.get("lat"),
                    "lon": city_info.get("lon"),
                    "ip": public_ip,
                })
        
        return jsonify({
            "ok": True,
            "city": "上海",
            "country": "中国",
            "ip": "本地开发环境",
            "message": "无法获取公网IP，已默认使用上海",
        })
    
    city_info = resolve_city_from_ip(client_ip)
    if city_info:
        city_name = get_city_name(city_info)
        translated_name = translate_city_name(city_name) if city_name else None
        return jsonify({
            "ok": True,
            "city": translated_name or city_name,
            "country": city_info.get("country"),
            "lat": city_info.get("lat"),
            "lon": city_info.get("lon"),
            "ip": client_ip,
        })
    
    return jsonify({"ok": False, "message": "无法识别当前城市"}), 404


@app.get("/api/weather")
def api_weather():
    city = (request.args.get("city") or "").strip()
    if not city:
        return jsonify({"ok": False, "message": "请输入城市名，例如：北京、上海、深圳"}), 400

    api_key = get_api_key()
    url = "https://api.weatherapi.com/v1/forecast.json"
    
    translated_city = translate_city_name(city)

    try:
        resp = requests.get(
            url,
            params={
                "key": api_key,
                "q": translated_city,
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

    city_name = location.get("name") or city
    chinese_city_name = get_chinese_city_name(city_name)
    
    result = {
        "ok": True,
        "city": chinese_city_name,
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
    app.run(host="0.0.0.0", port=5001, debug=True)
