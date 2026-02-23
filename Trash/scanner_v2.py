import asyncio
import base64
import json
import re
import time
import urllib.request

INPUT_FILE = "Trash/Test.txt"
OUTPUT_FILE = "main/final.txt"
MY_TAG = "@SwagMeli"

def get_flag(country_code):
    if not country_code or country_code == "UN": return "🌐"
    OFFSET = 127397
    return chr(ord(country_code[0].upper()) + OFFSET) + chr(ord(country_code[1].upper()) + OFFSET)

def get_geo(ip):
    try:
        # استفاده از API بدون معطلی زیاد
        url = f"http://ip-api.com/json/{ip}?fields=status,countryCode,country"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode())
            if data.get('status') == 'success':
                return data.get('countryCode', 'UN'), data.get('country', 'Unknown')
    except: pass
    return "UN", "Unknown"

async def main():
    print(f"🚀 شروع اسکنر با قابلیت تشخیص متن...")
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    except:
        print("❌ فایل Test.txt پیدا نشد!")
        return

    # این ریجکس الان خیلی قوی‌تر شده و هر چیزی که پروتکل وی‌پی‌ان داشته باشه رو شکار می‌کنه
    pattern = r'(vless|vmess|trojan|ss)://[^\s|#|\'|"|`|<>]+'
    configs = re.findall(pattern, content)
    
    print(f"🔎 تعداد {len(configs)} کانفیگ خام پیدا شد.")
    
    final_configs = []
    for config in configs:
        # استخراج هاست برای تشخیص کشور (حتی اگر پورت نداشته باشه)
        host_match = re.search(r'@([^:/#?]+)', config)
        if not host_match: continue
        host = host_match.group(1)
        
        # تشخیص کشور
        cc, cn = get_geo(host)
        flag = get_flag(cc)
        new_name = f"{flag} {cn} | {MY_TAG}"
        
        # بازسازی لینک با اسم جدید
        proto = config.split("://")[0]
        if proto == "vmess":
            try:
                v_body = config.split("://")[1].split("#")[0]
                v_body += "=" * ((4 - len(v_body) % 4) % 4)
                v_data = json.loads(base64.b64decode(v_body).decode())
                v_data['ps'] = new_name
                new_link = "vmess://" + base64.b64encode(json.dumps(v_data).encode()).decode()
                final_configs.append(new_link)
            except: continue
        else:
            clean_link = config.split("#")[0]
            final_configs.append(f"{clean_link}#{new_name}")

    if final_configs:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(final_configs))
        print(f"✅ {len(final_configs)} کانفیگ با موفقیت در final.txt ذخیره شد.")
    else:
        print("❓ عجیبه! هنوز هیچ کانفیگی استخراج نشد. متن فایل Test.txt رو چک کن.")

if __name__ == "__main__":
    asyncio.run(main())
