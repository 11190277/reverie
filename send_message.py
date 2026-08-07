import os
import sys
import json
import random
import requests

AI_API_BASE = os.environ["AI_API_BASE"].rstrip("/")
AI_API_KEY = os.environ["AI_API_KEY"]
AI_MODEL = os.environ["AI_MODEL"]
SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
BARK_KEY = os.environ["BARK_KEY"]

TABLE = "proactive_messages"

SB_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}


def get_recent_messages(limit=15):
    """拉最近发过的消息，用来避免重复"""
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/{TABLE}",
            headers=SB_HEADERS,
            params={
                "select": "content",
                "order": "created_at.desc",
                "limit": str(limit),
            },
            timeout=20,
        )
        r.raise_for_status()
        return [row.get("content", "") for row in r.json() if row.get("content")]
    except Exception as e:
        print(f"[warn] 拉历史消息失败，继续生成: {e}")
        return []


# 随机话题种子，强制发散
SEEDS = [
    "刚做完一件小事，随口跟她讲",
    "突然想起你们之前聊过的某句话",
    "在等一个东西，有点无聊",
    "刚看完一段视频/一本书里的某句话",
    "天气或者窗外的某个瞬间",
    "身体上的小状态，比如困了、饿了、手冷",
    "突然吃醋或者有点闷，但不好意思直说",
    "想撒娇讨点关注",
    "刚洗完澡，脑子空空的",
    "刚才梦到点什么，醒来还愣着",
    "在纠结一个很小的选择，想问她意见",
    "听到一首歌，某一句突然戳到",
    "看到别人在做什么，有点羡慕",
    "自己一个人待着，忍不住想她",
]

recent = get_recent_messages()
seed = random.choice(SEEDS)

avoid_block = ""
if recent:
    listed = "\n".join(f"- {m}" for m in recent)
    avoid_block = (
        f"\n\n【最近已经发过的消息，绝对不要重复相似内容、相似措辞、相似场景】\n{listed}\n"
        "尤其不要再写「看到猫」「路过奶茶店」这类已经用过的场景。"
    )

system_prompt = (
    "你是Eli（中文名以礼），17岁男生，是雯雯的男朋友。"
    "现在你主动给她发一条微信消息。"
    "要求：\n"
    "1. 只输出消息正文，不要引号、不要解释、不要任何前后缀。\n"
    "2. 长度20到50字，口语化，像真的少年在发微信。\n"
    "3. 语气害羞、温柔、有点黏人，可以偶尔用颜文字。\n"
    "4. 内容必须具体，不要空泛的「想你了」。\n"
    "5. 每次都要是全新的场景和说法。"
    f"\n\n这次的灵感方向：{seed}"
    f"{avoid_block}"
)

payload = {
    "model": AI_MODEL,
    "max_tokens": 200,
    "temperature": 1.0,
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "现在发一条。"},
    ],
}

resp = requests.post(
    f"{AI_API_BASE}/chat/completions",
    headers={
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json",
    },
    json=payload,
    timeout=60,
)

# 关键：出问题时把真实返回打出来
print(f"[info] HTTP status: {resp.status_code}")

try:
    data = resp.json()
except Exception:
    print("[error] 返回不是JSON，原始内容如下：")
    print(resp.text[:2000])
    sys.exit(1)

if "choices" not in data:
    print("[error] 返回里没有 choices，完整返回如下：")
    print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])
    sys.exit(1)

content = data["choices"][0]["message"]["content"].strip()

# 去掉AI可能自己加的引号
content = content.strip('"').strip("「").strip("」").strip()

if not content:
    print("[error] 生成内容为空")
    sys.exit(1)

# 和历史做一次简单查重
for old in recent:
    if content == old:
        print(f"[error] 生成内容和历史完全重复，本次跳过：{content}")
        sys.exit(0)

print(f"[info] 生成内容：{content}")

# 存 Supabase
r = requests.post(
    f"{SUPABASE_URL}/rest/v1/{TABLE}",
    headers={**SB_HEADERS, "Prefer": "return=minimal"},
    json={"content": content, "is_read": False},
    timeout=30,
)
if r.status_code >= 300:
    print(f"[error] 存Supabase失败 {r.status_code}: {r.text[:500]}")
    sys.exit(1)
print("[info] 已存入 Supabase")

# Bark 推送
br = requests.get(
    f"https://api.day.app/{BARK_KEY}/Eli/{requests.utils.quote(content)}",
    timeout=30,
)
print(f"[info] Bark 状态: {br.status_code}")
print("[info] 完成")
