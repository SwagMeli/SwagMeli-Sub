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
        # استفاده از تایم‌اوت بیشتر برای API
        url = f"http://ip-api.com/json/{ip}?fields=status,country,countryCode"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            if data.get('status') == 'success':
                return data.get('countryCode', 'UN'), data.get('country', 'Unknown')
    except: pass
    return "UN", "Unknown"

async def main():
    print(f"🚀 شروع پردازش بدون فیلتر پینگ برای تست...")
    try:
        with open(INPUT_FILE, "r") as f:
            content = f.read()
    except:
        print("❌ فایل ورودی پیدا نشد")
        return

    pattern = r'(vless|vmess|trojan|ss)://[^\s|#|\'|"]+'
    configs = re.findall(pattern, content)
    final_configs = []

    for config in configs:
        # استخراج Host
        parts = re.search(r'@([^:/]+):(\d+)', config)
        if not parts: continue
        host = parts.group(1)
        proto = config.split("://")[0]

        # در این نسخه تست، چک کردن پینگ رو حذف کردیم تا مطمئن بشیم خروجی میده
        cc, cn = get_geo(host)
        flag = get_flag(cc)
        new_name = f"{flag} {cn} | {MY_TAG}"
        
        if proto == "vmess":
            try:
                v_body = config.split("://")[1].split("#")[0]
                v_body += "=" * ((4 - len(v_body) % 4) % 4)
                v_data = json.loads(base64.b64decode(v_body).decode())
                v_data['ps'] = new_name
                new_link = "vmess://" + base64.b64encode(json.dumps(v_data).encode()).decode()
            except: continue
        else:
            clean_link = config.split("#")[0]
            new_link = f"{clean_link}#{new_name}"
        
        final_configs.append(new_link)
        print(f"✅ پردازش شد: {cn}")

    if final_configs:
        with open(OUTPUT_FILE, "w") as f:
            f.write("\n".join(final_configs))
        print(f"✨ تعداد {len(final_configs)} کانفیگ با موفقیت در {OUTPUT_FILE} ذخیره شد.")
    else:
        print("❌ هیچ کانفیگی پیدا نشد.")

if __name__ == "__main__":
    asyncio.run(main())
