from __future__ import annotations

import os
import random
from datetime import datetime

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

DEFAULT_AMAP_KEY = "c12b7299afb6d4b7e42d8cd0308045c6"


def get_amap_key() -> str:
    return os.getenv("AMAP_KEY", DEFAULT_AMAP_KEY).strip()


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


def get_city_by_amap_ip(ip=None):
    amap_key = get_amap_key()
    if not amap_key or amap_key == "你的高德地图API Key":
        return None
    
    try:
        params = {"key": amap_key, "output": "JSON"}
        if ip:
            params["ip"] = ip
        
        resp = requests.get(
            "https://restapi.amap.com/v3/ip",
            params=params,
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "1":
                return {
                    "city": data.get("city"),
                    "province": data.get("province"),
                    "country": data.get("country"),
                    "lat": None,
                    "lon": None,
                }
    except requests.RequestException:
        pass
    return None


@app.get("/api/location")
def api_location():
    client_ip = request.remote_addr
    
    if client_ip in ("127.0.0.1", "localhost", "::1"):
        public_ip = get_public_ip()
        if public_ip:
            city_info = get_city_by_amap_ip(public_ip)
            if city_info and city_info.get("city"):
                return jsonify({
                    "ok": True,
                    "city": city_info.get("city"),
                    "country": city_info.get("country"),
                    "lat": city_info.get("lat"),
                    "lon": city_info.get("lon"),
                    "ip": public_ip,
                })
            
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
    
    city_info = get_city_by_amap_ip(client_ip)
    if city_info and city_info.get("city"):
        return jsonify({
            "ok": True,
            "city": city_info.get("city"),
            "country": city_info.get("country"),
            "lat": city_info.get("lat"),
            "lon": city_info.get("lon"),
            "ip": client_ip,
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


CITY_COORDS = {
    "北京": {"lat": 39.9042, "lon": 116.4074, "province": "北京市"},
    "北京市": {"lat": 39.9042, "lon": 116.4074, "province": "北京市"},
    "上海": {"lat": 31.2304, "lon": 121.4737, "province": "上海市"},
    "上海市": {"lat": 31.2304, "lon": 121.4737, "province": "上海市"},
    "广州": {"lat": 23.1291, "lon": 113.2644, "province": "广东省"},
    "广州市": {"lat": 23.1291, "lon": 113.2644, "province": "广东省"},
    "深圳": {"lat": 22.5431, "lon": 114.0579, "province": "广东省"},
    "深圳市": {"lat": 22.5431, "lon": 114.0579, "province": "广东省"},
    "杭州": {"lat": 30.2741, "lon": 120.1551, "province": "浙江省"},
    "杭州市": {"lat": 30.2741, "lon": 120.1551, "province": "浙江省"},
    "成都": {"lat": 30.5728, "lon": 104.0668, "province": "四川省"},
    "成都市": {"lat": 30.5728, "lon": 104.0668, "province": "四川省"},
    "南京": {"lat": 32.0603, "lon": 118.7969, "province": "江苏省"},
    "南京市": {"lat": 32.0603, "lon": 118.7969, "province": "江苏省"},
    "武汉": {"lat": 30.5928, "lon": 114.3055, "province": "湖北省"},
    "武汉市": {"lat": 30.5928, "lon": 114.3055, "province": "湖北省"},
    "西安": {"lat": 34.3416, "lon": 108.9398, "province": "陕西省"},
    "西安市": {"lat": 34.3416, "lon": 108.9398, "province": "陕西省"},
    "重庆": {"lat": 29.4316, "lon": 106.9123, "province": "重庆市"},
    "重庆市": {"lat": 29.4316, "lon": 106.9123, "province": "重庆市"},
    "天津": {"lat": 39.0842, "lon": 117.2009, "province": "天津市"},
    "天津市": {"lat": 39.0842, "lon": 117.2009, "province": "天津市"},
    "苏州": {"lat": 31.2990, "lon": 120.5853, "province": "江苏省"},
    "苏州市": {"lat": 31.2990, "lon": 120.5853, "province": "江苏省"},
    "长沙": {"lat": 28.2280, "lon": 112.9388, "province": "湖南省"},
    "长沙市": {"lat": 28.2280, "lon": 112.9388, "province": "湖南省"},
    "郑州": {"lat": 34.7466, "lon": 113.6253, "province": "河南省"},
    "郑州市": {"lat": 34.7466, "lon": 113.6253, "province": "河南省"},
    "青岛": {"lat": 36.0671, "lon": 120.3826, "province": "山东省"},
    "青岛市": {"lat": 36.0671, "lon": 120.3826, "province": "山东省"},
    "厦门": {"lat": 24.4798, "lon": 118.0894, "province": "福建省"},
    "厦门市": {"lat": 24.4798, "lon": 118.0894, "province": "福建省"},
    "大连": {"lat": 38.9140, "lon": 121.6147, "province": "辽宁省"},
    "大连市": {"lat": 38.9140, "lon": 121.6147, "province": "辽宁省"},
    "沈阳": {"lat": 41.8057, "lon": 123.4315, "province": "辽宁省"},
    "沈阳市": {"lat": 41.8057, "lon": 123.4315, "province": "辽宁省"},
    "哈尔滨": {"lat": 45.8038, "lon": 126.5349, "province": "黑龙江省"},
    "哈尔滨市": {"lat": 45.8038, "lon": 126.5349, "province": "黑龙江省"},
    "福州": {"lat": 26.0745, "lon": 119.2965, "province": "福建省"},
    "福州市": {"lat": 26.0745, "lon": 119.2965, "province": "福建省"},
    "南宁": {"lat": 22.8170, "lon": 108.3665, "province": "广西壮族自治区"},
    "南宁市": {"lat": 22.8170, "lon": 108.3665, "province": "广西壮族自治区"},
    "昆明": {"lat": 24.8820, "lon": 102.8329, "province": "云南省"},
    "昆明市": {"lat": 24.8820, "lon": 102.8329, "province": "云南省"},
    "贵阳": {"lat": 26.6476, "lon": 106.6303, "province": "贵州省"},
    "贵阳市": {"lat": 26.6476, "lon": 106.6303, "province": "贵州省"},
    "兰州": {"lat": 36.0611, "lon": 103.8343, "province": "甘肃省"},
    "兰州市": {"lat": 36.0611, "lon": 103.8343, "province": "甘肃省"},
    "银川": {"lat": 38.4871, "lon": 106.2307, "province": "宁夏回族自治区"},
    "银川市": {"lat": 38.4871, "lon": 106.2307, "province": "宁夏回族自治区"},
    "西宁": {"lat": 36.6171, "lon": 101.7782, "province": "青海省"},
    "西宁市": {"lat": 36.6171, "lon": 101.7782, "province": "青海省"},
    "乌鲁木齐": {"lat": 43.8256, "lon": 87.6168, "province": "新疆维吾尔自治区"},
    "乌鲁木齐市": {"lat": 43.8256, "lon": 87.6168, "province": "新疆维吾尔自治区"},
    "呼和浩特": {"lat": 40.8423, "lon": 111.7510, "province": "内蒙古自治区"},
    "呼和浩特市": {"lat": 40.8423, "lon": 111.7510, "province": "内蒙古自治区"},
    "拉萨": {"lat": 29.6540, "lon": 91.1765, "province": "西藏自治区"},
    "拉萨市": {"lat": 29.6540, "lon": 91.1765, "province": "西藏自治区"},
    "海口": {"lat": 20.0440, "lon": 110.2242, "province": "海南省"},
    "海口市": {"lat": 20.0440, "lon": 110.2242, "province": "海南省"},
}


def find_city_by_coords(lat, lon):
    min_dist = float("inf")
    closest_city = "未知城市"
    for city, coords in CITY_COORDS.items():
        dist = (lat - coords["lat"])**2 + (lon - coords["lon"])**2
        if dist < min_dist:
            min_dist = dist
            closest_city = city
    return closest_city


def geocode_city(city_name):
    if city_name in CITY_COORDS:
        coords = CITY_COORDS[city_name]
        return {
            "lat": coords["lat"],
            "lon": coords["lon"],
            "city": city_name,
            "province": coords["province"],
        }
    
    amap_key = get_amap_key()
    if not amap_key or amap_key == "你的高德地图API Key":
        return None
    
    try:
        resp = requests.get(
            "https://restapi.amap.com/v3/geocode/geo",
            params={
                "key": amap_key,
                "address": city_name,
                "output": "JSON",
            },
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "1" and data.get("geocodes"):
                geocode = data["geocodes"][0]
                location = geocode.get("location", "").split(",")
                if len(location) == 2:
                    district = geocode.get("district")
                    amap_city = geocode.get("city")
                    
                    if district and district != amap_city:
                        display_name = district
                    elif amap_city:
                        display_name = amap_city
                    else:
                        display_name = city_name
                    
                    return {
                        "lat": float(location[1]),
                        "lon": float(location[0]),
                        "city": display_name,
                        "province": geocode.get("province"),
                    }
    except requests.RequestException:
        pass
    
    for key, coords in CITY_COORDS.items():
        if key in city_name or city_name in key:
            return {
                "lat": coords["lat"],
                "lon": coords["lon"],
                "city": key,
                "province": coords["province"],
            }
    
    return None


def reverse_geocode(lat, lon):
    amap_key = get_amap_key()
    if not amap_key or amap_key == "你的高德地图API Key":
        return None
    
    try:
        resp = requests.get(
            "https://restapi.amap.com/v3/geocode/regeo",
            params={
                "key": amap_key,
                "location": f"{lon},{lat}",
                "output": "JSON",
                "extensions": "base",
            },
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "1" and data.get("regeocode"):
                regeocode = data["regeocode"]
                address_component = regeocode.get("addressComponent", {})
                
                province = address_component.get("province")
                city = address_component.get("city")
                district = address_component.get("district")
                street = address_component.get("street")
                township = address_component.get("township")
                
                location_parts = []
                
                if city and city != province:
                    location_parts.append(city)
                
                if district and district != city:
                    location_parts.append(district)
                
                if township and township not in location_parts:
                    location_parts.append(township)
                
                if street:
                    location_parts.append(street)
                
                if not location_parts:
                    if province:
                        location_parts.append(province)
                    elif city:
                        location_parts.append(city)
                    else:
                        return {"city": "未知位置", "province": province}
                
                full_location = "".join(location_parts)
                
                return {
                    "city": full_location,
                    "province": province,
                }
    except requests.RequestException:
        pass
    return None


def get_weather_by_coords(lat, lon):
    try:
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code,is_day",
                "hourly": "temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m,precipitation_probability",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min",
                "forecast_days": 8,
                "timezone": "Asia/Shanghai",
                "units": "metric",
            },
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json()
    except requests.RequestException:
        pass
    return None


def get_air_quality(lat, lon):
    try:
        resp = requests.get(
            "https://air-quality-api.open-meteo.com/v1/air-quality",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "us_aqi",
                "timezone": "Asia/Shanghai",
            },
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json()
    except requests.RequestException:
        pass
    return None


WMO_WEATHER_CODES = {
    0: {"text": "晴", "icon": "sunny"},
    1: {"text": "晴", "icon": "sunny"},
    2: {"text": "多云", "icon": "cloudy"},
    3: {"text": "阴", "icon": "cloudy"},
    45: {"text": "雾", "icon": "fog"},
    48: {"text": "雾凇", "icon": "fog"},
    51: {"text": "毛毛雨", "icon": "rainy"},
    53: {"text": "小雨", "icon": "rainy"},
    55: {"text": "小雨", "icon": "rainy"},
    56: {"text": "冻毛毛雨", "icon": "rainy"},
    57: {"text": "冻毛毛雨", "icon": "rainy"},
    61: {"text": "小雨", "icon": "rainy"},
    63: {"text": "中雨", "icon": "rainy"},
    65: {"text": "大雨", "icon": "rainy"},
    66: {"text": "冻雨", "icon": "rainy"},
    67: {"text": "冻雨", "icon": "rainy"},
    71: {"text": "小雪", "icon": "snowy"},
    73: {"text": "小雪", "icon": "snowy"},
    75: {"text": "大雪", "icon": "snowy"},
    77: {"text": "雪粒", "icon": "snowy"},
    80: {"text": "阵雨", "icon": "rainy"},
    81: {"text": "阵雨", "icon": "rainy"},
    82: {"text": "强阵雨", "icon": "rainy"},
    85: {"text": "阵雪", "icon": "snowy"},
    86: {"text": "阵雪", "icon": "snowy"},
    95: {"text": "雷暴", "icon": "storm"},
    96: {"text": "雷暴", "icon": "storm"},
    99: {"text": "雷暴", "icon": "storm"},
}


def get_weather_condition(code):
    return WMO_WEATHER_CODES.get(code, {"text": "未知", "icon": "cloudy"})


def aqi_to_epa_index(aqi):
    if aqi <= 50:
        return 1
    elif aqi <= 100:
        return 2
    elif aqi <= 150:
        return 3
    elif aqi <= 200:
        return 4
    elif aqi <= 300:
        return 5
    else:
        return 6


@app.get("/api/weather")
def api_weather():
    city = (request.args.get("city") or "").strip()
    if not city:
        return jsonify({"ok": False, "message": "请输入城市名，例如：北京、上海、深圳"}), 400

    lat = None
    lon = None
    city_name = city
    province = None

    if "," in city and len(city.split(",")) == 2:
        try:
            parts = city.split(",")
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())
            
            reverse_result = reverse_geocode(lat, lon)
            if reverse_result:
                city_name = reverse_result.get("city") or "未知城市"
                province = reverse_result.get("province")
            else:
                city_name = find_city_by_coords(lat, lon)
        except ValueError:
            pass

    if lat is None or lon is None:
        geocode_result = geocode_city(city)
        if geocode_result:
            lat = geocode_result["lat"]
            lon = geocode_result["lon"]
            city_name = geocode_result.get("city") or city
            province = geocode_result.get("province")
        else:
            return jsonify({"ok": False, "message": f"无法定位城市 '{city}'，请检查城市名是否正确"}), 404

    weather_data = get_weather_by_coords(lat, lon)
    if not weather_data:
        return jsonify({"ok": False, "message": "获取天气数据失败，请稍后重试"}), 502

    air_data = get_air_quality(lat, lon)

    current = weather_data.get("current", {})
    hourly = weather_data.get("hourly", {})
    daily = weather_data.get("daily", {})

    condition_code = current.get("weather_code", 0)
    condition = get_weather_condition(condition_code)

    aqi = {"value": None, "level": 1}
    if air_data and air_data.get("current"):
        aq = air_data["current"]
        aqi_value = aq.get("us_aqi")
        aqi = {
            "value": aqi_value,
            "level": aqi_to_epa_index(aqi_value or 0),
            "pm2_5": aq.get("pm25"),
            "pm10": aq.get("pm10"),
            "o3": aq.get("o3"),
            "no2": aq.get("no2"),
            "so2": aq.get("so2"),
            "co": aq.get("co"),
        }

    result = {
        "ok": True,
        "city": city_name,
        "country": "中国",
        "region": province,
        "localtime": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "current": {
            "temp_c": current.get("temperature_2m"),
            "feelslike_c": current.get("apparent_temperature"),
            "humidity": current.get("relative_humidity_2m"),
            "wind_kph": current.get("wind_speed_10m"),
            "is_day": current.get("is_day"),
            "condition": condition["text"],
            "condition_icon": condition["icon"],
            "condition_code": condition_code,
        },
        "aqi": aqi,
        "forecast": [],
        "hourly": [],
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }

    if daily and daily.get("time"):
        for i in range(len(daily["time"])):
            date = daily["time"][i]
            max_temp = daily.get("temperature_2m_max", [])[i]
            min_temp = daily.get("temperature_2m_min", [])[i]
            day_condition_code = daily.get("weather_code", [])[i]
            day_condition = get_weather_condition(day_condition_code)
            result["forecast"].append({
                "date": date,
                "max_temp": max_temp,
                "min_temp": min_temp,
                "condition": day_condition["text"],
            })

    if hourly and hourly.get("time"):
        for i in range(len(hourly["time"])):
            time_str = hourly["time"][i]
            temp = hourly.get("temperature_2m", [])[i]
            h_condition_code = hourly.get("weather_code", [])[i]
            h_condition = get_weather_condition(h_condition_code)
            wind = hourly.get("wind_speed_10m", [])[i]
            humidity = hourly.get("relative_humidity_2m", [])[i]
            rain_chance = hourly.get("precipitation_probability", [])[i]
            result["hourly"].append({
                "time": time_str.replace("T", " "),
                "temp_c": temp,
                "condition": h_condition["text"],
                "wind_kph": wind,
                "humidity": humidity,
                "chance_of_rain": rain_chance,
            })

    condition_text = result["current"]["condition"]
    temp_c = result["current"]["temp_c"]
    date_str = datetime.now().strftime("%Y-%m-%d")
    result["fortune"] = get_tarot_fortune(condition_text, temp_c, date_str)

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
