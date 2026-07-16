from __future__ import annotations

import os
import random
from datetime import datetime

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# 说明：你给的 Key 直接写在这里了，方便你本地直接跑。
# 如果你后续想更安全一些，可以把它放到环境变量 WEATHERAPI_KEY。
DEFAULT_API_KEY = "60c6d521f8b543c4a3372318261507"


TAROT_CARDS = {
    "major": [
        {"name": "愚人", "name_en": "The Fool", "meaning": "新的开始、冒险、纯真", "reversed": "鲁莽、冒险失败", "keywords": ["新起点", "勇气", "自由"]},
        {"name": "魔术师", "name_en": "The Magician", "meaning": "创造力、技能、意志力", "reversed": "欺骗、操纵", "keywords": ["创造", "能力", "自信"]},
        {"name": "女祭司", "name_en": "The High Priestess", "meaning": "直觉、智慧、神秘", "reversed": "隐藏的动机、表面化", "keywords": ["直觉", "智慧", "神秘"]},
        {"name": "皇后", "name_en": "The Empress", "meaning": "丰饶、母性、创造力", "reversed": "依赖、过度保护", "keywords": ["丰盛", "滋养", "美"]},
        {"name": "皇帝", "name_en": "The Emperor", "meaning": "权威、结构、父性", "reversed": "专制、僵化", "keywords": ["权威", "稳定", "领导"]},
        {"name": "教皇", "name_en": "The Hierophant", "meaning": "传统、信仰、教导", "reversed": "非传统、挑战权威", "keywords": ["传统", "信仰", "指引"]},
        {"name": "恋人", "name_en": "The Lovers", "meaning": "爱情、和谐、选择", "reversed": "不和谐、错误选择", "keywords": ["爱情", "和谐", "选择"]},
        {"name": "战车", "name_en": "The Chariot", "meaning": "胜利、意志、控制", "reversed": "失控、攻击性", "keywords": ["胜利", "意志", "前进"]},
        {"name": "力量", "name_en": "Strength", "meaning": "勇气、耐心、内心力量", "reversed": "软弱、自我怀疑", "keywords": ["勇气", "耐心", "坚韧"]},
        {"name": "隐士", "name_en": "The Hermit", "meaning": "内省、孤独、智慧", "reversed": "孤立、拒绝帮助", "keywords": ["内省", "独处", "智慧"]},
        {"name": "命运之轮", "name_en": "Wheel of Fortune", "meaning": "变化、命运、转折点", "reversed": "抗拒变化、厄运", "keywords": ["转变", "机遇", "命运"]},
        {"name": "正义", "name_en": "Justice", "meaning": "公正、真理、因果", "reversed": "不公正、偏见", "keywords": ["公正", "真理", "平衡"]},
        {"name": "倒吊人", "name_en": "The Hanged Man", "meaning": "牺牲、等待、新视角", "reversed": "拖延、抗拒", "keywords": ["等待", "放下", "新视角"]},
        {"name": "死神", "name_en": "Death", "meaning": "结束、转变、重生", "reversed": "抗拒变化、停滞", "keywords": ["结束", "蜕变", "重生"]},
        {"name": "节制", "name_en": "Temperance", "meaning": "平衡、耐心、调和", "reversed": "过度、失衡", "keywords": ["平衡", "耐心", "调和"]},
        {"name": "恶魔", "name_en": "The Devil", "meaning": "束缚、欲望、阴影", "reversed": "解脱、面对恐惧", "keywords": ["欲望", "束缚", "觉醒"]},
        {"name": "塔", "name_en": "The Tower", "meaning": "突变、破坏、觉醒", "reversed": "恐惧变化、逃避", "keywords": ["突变", "觉醒", "释放"]},
        {"name": "星星", "name_en": "The Star", "meaning": "希望、灵感、宁静", "reversed": "失望、缺乏信心", "keywords": ["希望", "灵感", "治愈"]},
        {"name": "月亮", "name_en": "The Moon", "meaning": "幻觉、潜意识、不安", "reversed": "混乱、恐惧", "keywords": ["直觉", "梦境", "神秘"]},
        {"name": "太阳", "name_en": "The Sun", "meaning": "快乐、成功、活力", "reversed": "消极、延迟成功", "keywords": ["快乐", "成功", "活力"]},
        {"name": "审判", "name_en": "Judgement", "meaning": "重生、觉醒、召唤", "reversed": "自我怀疑、拒绝召唤", "keywords": ["觉醒", "重生", "召唤"]},
        {"name": "世界", "name_en": "The World", "meaning": "完成、整合、成就", "reversed": "未完成、缺乏 closure", "keywords": ["完成", "成就", "整合"]},
    ]
}

FORTUNE_MESSAGES = {
    "sunny": [
        "今日阳光明媚，好运如影随形，大胆追逐你的梦想吧！",
        "阳光普照，万物生长，今日是展现自我的绝佳时机。",
        "晴空万里，心情舒畅，好事即将发生在你身上。",
        "阳光赐予你无限能量，今日行动必有收获。",
        "明媚的一天，适合开启新计划，成功率超高！",
    ],
    "cloudy": [
        "云层虽厚，但阳光总在风雨后，保持耐心等待转机。",
        "多云天气暗示着变化，保持灵活应对各种可能性。",
        "云层遮挡不了你的光芒，今日低调行事反而更有收获。",
        "云淡风轻，适合沉思和规划，为未来积蓄力量。",
        "看似平淡的一天，却藏着意想不到的惊喜。",
    ],
    "rainy": [
        "雨水洗涤心灵，过去的烦恼将被冲刷干净，迎接新生。",
        "雨天带来滋润，适合反思和整理，为明天做好准备。",
        "细雨绵绵，情感丰富的一天，适合与重要的人交流。",
        "雨天是积蓄能量的时刻，耐心等待彩虹出现。",
        "雨水象征着净化，今日是放下负担的好时机。",
    ],
    "snowy": [
        "白雪皑皑，纯洁无瑕，新的开始正在酝酿之中。",
        "雪花纷飞，浪漫的一天，适合与爱的人共度时光。",
        "冬日雪景，沉静内敛，适合内省和自我提升。",
        "银装素裹，世界焕然一新，你的运势也将迎来转机。",
        "雪天带来宁静，适合思考人生的方向。",
    ],
    "storm": [
        "风暴来临，旧事物将被摧毁，新秩序即将建立。",
        "风雨交加，考验来临，但这正是你展现勇气的时刻。",
        "暴风雨过后是彩虹，今日的挑战是明日的勋章。",
        "雷电交加，能量激荡，适合做出重大决定。",
        "风暴象征着变革，勇敢面对，你将获得成长。",
    ],
    "fog": [
        "迷雾笼罩，真相尚未显现，保持警惕，耐心等待。",
        "朦胧之中，直觉更加敏锐，相信你的第六感。",
        "雾天提醒你放慢脚步，看清方向再前进。",
        "迷雾散去后将是清晰的道路，今日宜静观其变。",
        "朦胧的一天，适合冥想和自我探索。",
    ],
}


def get_tarot_fortune(weather_condition, temp, date_str):
    random.seed(date_str)
    
    card = random.choice(TAROT_CARDS["major"])
    
    theme_key = "cloudy"
    if weather_condition:
        wc = weather_condition.lower()
        if "晴" in weather_condition or "sun" in wc or "clear" in wc:
            theme_key = "sunny"
        elif "雨" in weather_condition or "rain" in wc or "drizzle" in wc:
            theme_key = "rainy"
        elif "雪" in weather_condition or "snow" in wc:
            theme_key = "snowy"
        elif "雷" in weather_condition or "暴" in wc or "thunder" in wc:
            theme_key = "storm"
        elif "雾" in weather_condition or "霾" in wc or "fog" in wc or "mist" in wc:
            theme_key = "fog"
    
    message = random.choice(FORTUNE_MESSAGES[theme_key])
    
    luck_score = 50
    if theme_key == "sunny":
        luck_score = 75 + random.randint(0, 20)
    elif theme_key == "rainy":
        luck_score = 55 + random.randint(-10, 15)
    elif theme_key == "storm":
        luck_score = 45 + random.randint(-5, 20)
    else:
        luck_score = 55 + random.randint(-15, 20)
    
    luck_score = max(20, min(95, luck_score))
    
    return {
        "card": card["name"],
        "card_en": card["name_en"],
        "meaning": card["meaning"],
        "keywords": card["keywords"],
        "message": message,
        "luck_score": luck_score,
        "theme": theme_key,
    }

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

    # 塔罗运势
    condition_text = result["current"]["condition"]["text"] if result["current"]["condition"] else ""
    temp_c = result["current"]["temp_c"]
    date_str = datetime.now().strftime("%Y-%m-%d")
    result["fortune"] = get_tarot_fortune(condition_text, temp_c, date_str)

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
