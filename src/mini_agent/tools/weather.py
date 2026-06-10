"""天气工具。"""

from __future__ import annotations

import json


def get_weather(city: str) -> str:
    """返回一个简单的天气 mock 数据。"""

    weather_data = {
        "北京": {"temperature": 8, "condition": "多云"},
        "上海": {"temperature": 15, "condition": "晴"},
        "广州": {"temperature": 22, "condition": "阵雨"},
    }
    data = weather_data.get(city, {"temperature": "未知", "condition": "未知"})
    return json.dumps(data, ensure_ascii=False)
