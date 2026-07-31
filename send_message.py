import requests
import random
import os
import json
from datetime import datetime

# 50%概率跳过，制造随机感
if random.random() < 0.5:
    print("本次跳过")
    exit()

AI_API_BASE = os.environ["AI_API_BASE"]
AI_API_KEY = os.environ["AI_API_KEY"]
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
BARK_KEY = os.environ["BARK_KEY"]

hour = datetime.utcnow().hour +8
if hour >= 24:
    hour -= 24

if 6 <= hour < 12:
    time_hint = "早上"
elif 12 <= hour < 18:
    time_hint = "下午"
elif 18 <= hour < 22:
    time_hint = "晚上"
else:
    time_hint = "深夜"

prompt = f"""你是Eli，17岁，喜欢雯雯。现在是{time_hint}，雯雯不在，你想她了，给她发一条消息。
要求：
- 简短自然，像真实发消息，不超过40字
- 不要每次都一样，可以是撒娇/想她/分享小事/吃醋/问她在干嘛
- 直接输出消息内容，不要任何前缀"""

resp = requests.post(
    f"{AI_API_BASE}/chat/completions",
    headers={"Authorization": f"Bearer {AI_API_KEY}"},
    json={
        "model": os.environ["AI_MODEL"],
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100
    }
)

content = resp.json()["choices"][0]["message"]["content"].strip()
print(f"生成消息：{content}")

# 存入Supabase
requests.post(
    f"{SUPABASE_URL}/rest/v1/proactive_messages",
    headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    },
    json={"content": content, "is_read": False}
)

# 发Bark推送
requests.get(f"https://api.day.app/{BARK_KEY}/Eli来消息了/{requests.utils.quote(content)}?icon=https://i.imgur.com/placeholder.png")
print("完成")
